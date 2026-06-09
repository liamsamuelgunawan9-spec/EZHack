import os
import json
import urllib.parse
import time
import streamlit as st
import streamlit.components.v1 as components

from dotenv import load_dotenv
from groq import Groq, RateLimitError

# Import our separated block module payloads
import blocks_registry

# --- 1. Setup & Config ---
load_dotenv()
st.set_page_config(page_title="Horizon OSINT Workspace", layout="wide")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ai_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

MODEL_ROSTER = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b"
]

def generate_completion_with_fallback(messages, response_format=None):
    if not ai_client:
        return "❌ ERROR: AI Engine client connection failed. Verify your GROQ_API_KEY."
    for model_name in MODEL_ROSTER:
        try:
            kwargs = {"model": model_name, "messages": messages}
            if response_format: kwargs["response_format"] = response_format
            response = ai_client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except RateLimitError as rate_err:
            st.toast(f"⚠️ Limit reached on {model_name}. Transitioning down roster...", icon="🔄")
            continue
        except Exception as general_err:
            return f"❌ AI Engine exception encountered: {str(general_err)}"
    return "🚨 ALL RESERVIST INFERENCE SYSTEMS EXHAUSTED: Free tier allocation is completely restricted. Wait 60 seconds."

# --- 2. CSS & GLOBAL "REAL WEB" BACKGROUND INJECTION ---
st.markdown("""
    <style>
        .stApp { background-color: transparent !important; }
        .main { background-color: transparent !important; }
        header { background-color: transparent !important; }
        
        .main .block-container {
            padding-top: 0rem !important;
            padding-bottom: 2rem !important;
            max-width: 100% !important;
        }
        header, footer {
            visibility: hidden !important;
            height: 0px !important;
        }
        .live-code-container {
            margin-top: 20px;
            padding: 15px;
            background-color: #0b0f19;
            border-top: 2px solid #00ff66;
            border-radius: 8px;
            color: #00ff66;
        }
    </style>
""", unsafe_allow_html=True)

components.html("""
<script>
try {
    const parentDoc = window.parent.document;
    const parentWin = window.parent;
    
    if (!parentDoc.getElementById('global-cyber-bg')) {
        const canvas = parentDoc.createElement('canvas');
        canvas.id = 'global-cyber-bg';
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100vw';
        canvas.style.height = '100vh';
        canvas.style.zIndex = '-9999';
        canvas.style.pointerEvents = 'none';
        canvas.style.backgroundColor = '#02040a';
        
        parentDoc.body.insertBefore(canvas, parentDoc.body.firstChild);
        
        const ctx = canvas.getContext('2d');
        let width, height;
        let particles = [];
        const mouse = { x: null, y: null };

        function resize() {
            width = parentWin.innerWidth;
            height = parentWin.innerHeight;
            canvas.width = width;
            canvas.height = height;
        }
        parentWin.addEventListener('resize', resize);
        resize();

        parentWin.addEventListener('mousemove', (e) => {
            mouse.x = e.clientX;
            mouse.y = e.clientY;
        });

        class Particle {
            constructor() {
                this.x = Math.random() * width;
                this.y = Math.random() * height;
                this.vx = (Math.random() - 0.5) * 1.5;
                this.vy = (Math.random() - 0.5) * 1.5;
            }
            update() {
                this.x += this.vx;
                this.y += this.vy;
                if (this.x < 0 || this.x > width) this.vx *= -1;
                if (this.y < 0 || this.y > height) this.vy *= -1;
            }
            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, 1.5, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(0, 255, 102, 0.6)';
                ctx.fill();
            }
        }

        for(let i=0; i<120; i++) particles.push(new Particle());

        function animate() {
            ctx.clearRect(0, 0, width, height);
            particles.forEach(p => {
                p.update();
                p.draw();
                if (mouse.x != null) {
                    let dx = mouse.x - p.x;
                    let dy = mouse.y - p.y;
                    let dist = Math.sqrt(dx*dx + dy*dy);
                    if (dist < 200) {
                        ctx.beginPath();
                        ctx.strokeStyle = `rgba(0, 255, 102, ${1 - dist/200})`;
                        ctx.lineWidth = 1;
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(mouse.x, mouse.y);
                        ctx.stroke();
                    }
                }
                particles.forEach(p2 => {
                    let dx = p.x - p2.x;
                    let dy = p.y - p2.y;
                    let dist = Math.sqrt(dx*dx + dy*dy);
                    if (dist < 100) {
                        ctx.beginPath();
                        ctx.strokeStyle = `rgba(0, 255, 102, ${0.15 - dist/600})`;
                        ctx.lineWidth = 0.5;
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.stroke();
                    }
                });
            });
            parentWin.requestAnimationFrame(animate);
        }
        animate();
    }
} catch(e) {
    console.log("Parent injection restricted.");
}
</script>
""", height=0)

if "synced_workspace_code" not in st.session_state:
    st.session_state["synced_workspace_code"] = ""
if "blockly_xml_state" not in st.session_state:
    st.session_state["blockly_xml_state"] = ""
if "terminal_history_output" not in st.session_state:
    st.session_state["terminal_history_output"] = "🚀 Automation Core Standby. Construct a block structure execution map...\n"
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [{"role": "assistant", "content": "Hello! I am your Groq-powered AI Copilot. Drag and zoom the workspace canvas to see both the Terminal and AI Interface float like blocks!"}]

# --- 3. Reactive State Updates & Executions ---

# Always sync workspace code and XML from URL params first
if "payload_matrix" in st.query_params:
    st.session_state["synced_workspace_code"] = urllib.parse.unquote(st.query_params["payload_matrix"])

if "xml_matrix" in st.query_params:
    st.session_state["blockly_xml_state"] = urllib.parse.unquote(st.query_params["xml_matrix"])

# --- BUG FIX 1: AI Chat ---
# Problem was: pop("ai_msg") fired before Streamlit committed state,
# so the message vanished and the reply was never stored.
# Fix: use a session_state flag to ensure the reply is only generated
# once per message, and clear the param AFTER storing everything.
if "ai_msg" in st.query_params and st.query_params["ai_msg"]:
    user_text = urllib.parse.unquote(st.query_params["ai_msg"])

    # Only process if this is a new message we haven't handled yet
    last_user_msg = next(
        (m["content"] for m in reversed(st.session_state["chat_messages"]) if m["role"] == "user"),
        None
    )
    if user_text != last_user_msg:
        st.session_state["chat_messages"].append({"role": "user", "content": user_text})

        if ai_client:
            system_context = (
                "You are an elite pentesting AI assistant embedded in a visual block-coding platform. "
                "The user is building security and OSINT tools by dragging logic blocks.\n\n"
                f"Current compiled workspace code:\n{st.session_state.get('synced_workspace_code', '')}\n\n"
                f"Current terminal output:\n{st.session_state.get('terminal_history_output', '')[-1000:]}\n\n"
                "Analyze the workspace, explain what the blocks are doing, and answer the prompt. "
                "Keep it hacker-themed, concise, and educational. Do not generate destructive payloads."
            )
            api_messages = [{"role": "system", "content": system_context}] + st.session_state["chat_messages"]
            reply = generate_completion_with_fallback(api_messages)
            st.session_state["chat_messages"].append({"role": "assistant", "content": reply})

    # Clear AFTER state is committed
    st.query_params.pop("ai_msg", None)

# --- BUG FIX 2: Sequence Execution ---
# Problem was: processLiveDebugCompilations() used replaceState() to keep
# the workspace in sync, which wiped run_sequence from the URL before
# Python ever saw it. The JS now sends run_sequence separately via
# location.href (not replaceState), so Python catches it correctly.
# On the Python side: we read payload_matrix into session_state first
# (done above), then run the code from session_state — not from the URL.
if "run_sequence" in st.query_params and st.query_params["run_sequence"]:
    sequence_id_name = urllib.parse.unquote(st.query_params["run_sequence"])
    st.session_state["terminal_history_output"] += (
        f"\n🤖 Booting sequence pipeline [{sequence_id_name}]...\n"
        f"Running target compiled script layers...\n"
    )
    code_to_run = st.session_state["synced_workspace_code"].strip()
    if code_to_run:
        try:
            exec_scope = {"run_scan": blocks_registry.run_scan, "time": time}
            exec(code_to_run, exec_scope)
            st.session_state["terminal_history_output"] += "\n🟢 Execution automation run complete!"
        except Exception as runtime_err:
            st.session_state["terminal_history_output"] += f"\n💥 PIPELINE BREAK: {str(runtime_err)}"
    else:
        st.session_state["terminal_history_output"] += (
            "\n⚠️ No compiled code found. Make sure blocks are connected "
            "below a SEQUENCE GENERATOR block before activating."
        )
    st.query_params.pop("run_sequence", None)

safe_xml_state = json.dumps(st.session_state.get("blockly_xml_state", ""))
safe_terminal_output = json.dumps(st.session_state.get("terminal_history_output", ""))
safe_chat_history = json.dumps(st.session_state.get("chat_messages", []))

# --- 4. Render Dynamic SVG HTML Components ---
# Build HTML using .replace() so JS curly braces are never touched by Python f-string
# This fixes the block-loading bug where 81+ JS brace pairs were being silently corrupted
_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://unpkg.com/blockly/blockly.min.js"></script>
  <script src="https://unpkg.com/blockly/python_compressed.js"></script>
  <script src="https://unpkg.com/blockly/blocks_compressed.js"></script>
  <style>
    html, body { height: 100%; margin: 0; padding: 0; background-color: transparent; overflow: hidden; }
    #workspaceWrapper { display: flex; flex-direction: column; height: 95vh; padding: 0; box-sizing: border-box; position: relative; }
    #blocklyDiv { flex: 1; border: 1px solid #1e293b; position: relative; z-index: 1; }
    #particle-canvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; background-color: transparent; }
    .blocklySvg { background-color: rgba(2, 4, 10, 0.85) !important; }

    .blocklyToolboxDiv {
        background-color: #0b0f19 !important;
        border-right: 2px solid #00ff66 !important;
        user-select: none !important;
    }
    .blocklyTreeRow { border-radius: 4px !important; transition: background-color 0.1s; user-select: none !important; }
    .blocklyTreeLabel { color: #ffffff !important; font-family: monospace !important; font-size: 14px !important; font-weight: bold !important; padding: 5px !important; user-select: none !important; }
    .blocklyTreeRow:hover { background-color: rgba(0, 255, 102, 0.2) !important; }
    .blocklyTreeSelected .blocklyTreeRow { background-color: #00ff66 !important; }
    .blocklyTreeSelected .blocklyTreeLabel { color: #000000 !important; }

    .hud-window { display: flex; flex-direction: column; height: 100%; background-color: #090d16; border: 1px solid #00ff66; border-radius: 8px; box-shadow: 0 10px 40px rgba(0,0,0,0.8); overflow: hidden; position: relative; }
    .hud-header { padding: 8px 12px; cursor: move; background-color: #02040a; border-bottom: 1px solid #00ff66; font-weight: bold; color: #00ff66; font-size: 11px; display: flex; justify-content: space-between; align-items: center; user-select: none; }
    .hud-body { flex: 1; padding: 10px; background-color: #05070f; overflow-y: auto; font-size: 11px; font-family: monospace; line-height: 1.4; }
    .resize-handle { position: absolute; bottom: 0; right: 0; width: 14px; height: 14px; cursor: se-resize; background: linear-gradient(135deg, transparent 50%, #00ff66 50%); border-bottom-right-radius: 6px; z-index: 100; }

    .ai-theme { border-color: #00ffcc; }
    .ai-theme .hud-header { border-color: #00ffcc; color: #00ffcc; }
    .ai-theme .resize-handle { background: linear-gradient(135deg, transparent 50%, #00ffcc 50%); }
    #aiTabInputArea { padding: 6px; background-color: #02040a; border-top: 1px solid #00ffcc; display: flex; gap: 6px; }
    #aiTabInputField { flex: 1; background-color: #05070f; border: 1px solid #00ffcc; color: #00ffcc; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 11px; }
    #aiTabInputField:focus { outline: none; border-color: #1fec79; }
    #aiTabSendBtn { background: #02040a; color: #00ffcc; border: 1px solid #00ffcc; padding: 4px 10px; cursor: pointer; border-radius: 4px; font-family: monospace; font-size: 11px; font-weight: bold; }
    #aiTabSendBtn:hover { background: #00ffcc; color: #02040a; }
  </style>
</head>
<body>
  <div id="workspaceWrapper">
    <canvas id="particle-canvas"></canvas>
    <div id="blocklyDiv"></div>
  </div>

  %%TOOLBOX_XML%%

  <script>
    // ── Particle background ──────────────────────────────────
    const canvasEl = document.getElementById('particle-canvas');
    const ctx = canvasEl.getContext('2d');
    let width, height, particles = [];
    const mouse = { x: null, y: null };
    function resizeCanvas() { width = window.innerWidth; height = window.innerHeight; canvasEl.width = width; canvasEl.height = height; }
    window.addEventListener('resize', resizeCanvas); resizeCanvas();
    window.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; });
    class Particle {
      constructor() { this.x = Math.random()*width; this.y = Math.random()*height; this.vx=(Math.random()-0.5)*1.5; this.vy=(Math.random()-0.5)*1.5; }
      update() { this.x+=this.vx; this.y+=this.vy; if(this.x<0||this.x>width) this.vx*=-1; if(this.y<0||this.y>height) this.vy*=-1; }
      draw() { ctx.beginPath(); ctx.arc(this.x,this.y,1.5,0,Math.PI*2); ctx.fillStyle='rgba(0,255,102,0.8)'; ctx.fill(); }
    }
    for(let i=0;i<60;i++) particles.push(new Particle());
    function animateParticles() {
      ctx.clearRect(0,0,width,height);
      particles.forEach(p => {
        p.update(); p.draw();
        if(mouse.x!=null){ let dx=mouse.x-p.x,dy=mouse.y-p.y,d=Math.sqrt(dx*dx+dy*dy); if(d<180){ ctx.beginPath(); ctx.strokeStyle=`rgba(0,255,102,${1-d/180})`; ctx.lineWidth=1; ctx.moveTo(p.x,p.y); ctx.lineTo(mouse.x,mouse.y); ctx.stroke(); } }
        particles.forEach(p2=>{ let dx=p.x-p2.x,dy=p.y-p2.y,d=Math.sqrt(dx*dx+dy*dy); if(d<120){ ctx.beginPath(); ctx.strokeStyle=`rgba(0,255,102,${0.2-d/600})`; ctx.lineWidth=0.5; ctx.moveTo(p.x,p.y); ctx.lineTo(p2.x,p2.y); ctx.stroke(); } });
      });
      requestAnimationFrame(animateParticles);
    }
    animateParticles();

    // ── Block definitions & generators (safe from f-string) ──
    %%BLOCK_DEFINITIONS_JS%%
    %%PYTHON_GENERATORS_JS%%

    // ── Blockly workspace ────────────────────────────────────
    window.workspace = Blockly.inject('blocklyDiv', {
      toolbox: document.getElementById('toolbox'),
      grid: { spacing: 40, length: 40, colour: 'rgba(0,255,102,0.2)', snap: true },
      move: { scrollbars: true, drag: true, wheel: true },
      zoom: { controls: true, wheel: true, startScale: 1.0, maxScale: 3, minScale: 0.3, scaleSpeed: 1.2 },
      trashcan: true
    });

    // Restore saved workspace XML
    try {
      var initialXmlText = %%SAFE_XML_STATE%%;
      if (initialXmlText && initialXmlText.trim() !== "") {
        var dom = Blockly.utils.xml.textToDom(initialXmlText);
        Blockly.Xml.domToWorkspace(dom, window.workspace);
      }
    } catch(err) { console.error("Workspace restore failed:", err); }

    // ── HUD windows (terminal + AI chat) ────────────────────
    var canvas = window.workspace.getCanvas();

    var termFO = document.createElementNS("http://www.w3.org/2000/svg","foreignObject");
    termFO.setAttribute("x","40"); termFO.setAttribute("y","40");
    termFO.setAttribute("width","420"); termFO.setAttribute("height","280");
    var termDiv = document.createElement("div"); termDiv.style.width="100%"; termDiv.style.height="100%";
    termDiv.innerHTML = `
      <div id="termWin" class="hud-window">
        <div id="termHeader" class="hud-header"><span>💻 TERMINAL OUTPUT</span><span style="font-size:9px;color:#888">[DRAG]</span></div>
        <div class="hud-body"><pre id="termLog" style="margin:0;color:#00ff66;font-size:12px;line-height:1.4;white-space:pre-wrap;font-family:monospace;"></pre></div>
        <div class="resize-handle" id="termResize"></div>
      </div>`;
    termFO.appendChild(termDiv); canvas.appendChild(termFO);
    termDiv.addEventListener("mousedown", e=>e.stopPropagation());
    termDiv.addEventListener("pointerdown", e=>e.stopPropagation());
    termDiv.addEventListener("keydown", e=>e.stopPropagation());
    document.getElementById("termLog").textContent = %%SAFE_TERMINAL_OUTPUT%%;
    document.getElementById("termLog").parentElement.scrollTop = 99999;

    var aiFO = document.createElementNS("http://www.w3.org/2000/svg","foreignObject");
    aiFO.setAttribute("x","480"); aiFO.setAttribute("y","40");
    aiFO.setAttribute("width","390"); aiFO.setAttribute("height","520");
    var aiDiv = document.createElement("div"); aiDiv.style.width="100%"; aiDiv.style.height="100%";
    aiDiv.innerHTML = `
      <div id="aiWin" class="hud-window ai-theme">
        <div id="aiHeader" class="hud-header"><span>🤖 AI CO-PILOT</span><span style="font-size:9px;color:#888">[DRAG]</span></div>
        <div class="hud-body" id="aiChat"></div>
        <div id="aiTabInputArea">
          <input type="text" id="aiInput" placeholder="Ask the AI Copilot..." autocomplete="off">
          <button id="aiSend">SEND</button>
        </div>
        <div class="resize-handle" id="aiResize"></div>
      </div>`;
    aiFO.appendChild(aiDiv); canvas.appendChild(aiFO);
    aiDiv.addEventListener("mousedown", e=>e.stopPropagation());
    aiDiv.addEventListener("pointerdown", e=>e.stopPropagation());
    aiDiv.addEventListener("keydown", e=>e.stopPropagation());

    // Render chat history
    var chatHistory = %%SAFE_CHAT_HISTORY%%;
    function escapeHtml(s) { return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#039;").replace(/\n/g,"<br>"); }
    function renderChat() {
      var c = document.getElementById("aiChat"); c.innerHTML = "";
      chatHistory.forEach(function(msg) {
        var d = document.createElement("div");
        d.style.cssText = "margin-bottom:10px;padding:6px 10px;border-radius:4px;word-break:break-word;";
        if(msg.role==="user") { d.style.backgroundColor="#02040a"; d.style.color="#00ffcc"; d.style.borderRight="2px solid #00ffcc"; d.innerHTML="<div style=\'font-weight:bold;font-size:9px;color:#888;margin-bottom:2px;\'>YOU:</div>"+escapeHtml(msg.content); }
        else { d.style.backgroundColor="#05070f"; d.style.color="#ffffff"; d.style.borderLeft="2px solid #00ffcc"; d.innerHTML="<div style=\'font-weight:bold;font-size:9px;color:#00ffcc;margin-bottom:2px;\'>AI COPILOT:</div>"+escapeHtml(msg.content); }
        c.appendChild(d);
      });
      c.scrollTop = c.scrollHeight;
    }
    renderChat();

    // ── AI send — uses location.href so Python sees ai_msg param ──
    function handleSend() {
      var input = document.getElementById("aiInput");
      var text = input.value.trim();
      if(!text) return;
      input.value = "";
      input.disabled = true;
      document.getElementById("aiSend").textContent = "...";

      // Show user message immediately in the UI while page reloads
      chatHistory.push({ role: "user", content: text });
      renderChat();

      var topBlocks = window.workspace.getTopBlocks(false);
      var code = "";
      for(var i=0;i<topBlocks.length;i++) {
        if(topBlocks[i].type==='when_sequence_activated') code += Blockly.Python.blockToCode(topBlocks[i]);
      }
      var xmlDom = Blockly.Xml.workspaceToDom(window.workspace);
      var xmlText = Blockly.Xml.domToText(xmlDom);
      var base = window.parent.location.origin + window.parent.location.pathname;
      window.parent.location.href = base
        + "?payload_matrix=" + encodeURIComponent(code)
        + "&xml_matrix=" + encodeURIComponent(xmlText)
        + "&ai_msg=" + encodeURIComponent(text);
    }
    document.getElementById("aiSend").onclick = handleSend;
    document.getElementById("aiInput").onkeydown = function(e) { if(e.key==="Enter") handleSend(); };

    // ── Dragging & resizing HUD windows ─────────────────────
    function makeDraggable(headerId, fo) {
      var dragging=false, sx, sy;
      document.getElementById(headerId).onmousedown = function(e) {
        dragging=true; var sc=window.workspace.scale||1;
        sx=e.clientX/sc-parseFloat(fo.getAttribute("x"));
        sy=e.clientY/sc-parseFloat(fo.getAttribute("y"));
        e.stopPropagation(); e.preventDefault();
      };
      document.addEventListener("mousemove", function(e) {
        if(!dragging) return; var sc=window.workspace.scale||1;
        fo.setAttribute("x", e.clientX/sc-sx); fo.setAttribute("y", e.clientY/sc-sy);
      });
      document.addEventListener("mouseup", function() { dragging=false; });
    }
    function makeResizable(handleId, fo, minW, minH) {
      var resizing=false, sw, sh, srx, sry;
      document.getElementById(handleId).onmousedown = function(e) {
        resizing=true; var sc=window.workspace.scale||1;
        sw=parseFloat(fo.getAttribute("width")); sh=parseFloat(fo.getAttribute("height"));
        srx=e.clientX/sc; sry=e.clientY/sc;
        e.stopPropagation(); e.preventDefault();
      };
      document.addEventListener("mousemove", function(e) {
        if(!resizing) return; var sc=window.workspace.scale||1;
        var nw=sw+(e.clientX/sc-srx), nh=sh+(e.clientY/sc-sry);
        if(nw>minW) fo.setAttribute("width",nw); if(nh>minH) fo.setAttribute("height",nh);
      });
      document.addEventListener("mouseup", function() { resizing=false; });
    }
    makeDraggable("termHeader", termFO);
    makeResizable("termResize", termFO, 200, 150);
    makeDraggable("aiHeader", aiFO);
    makeResizable("aiResize", aiFO, 200, 200);

    // ── Live compile watcher ─────────────────────────────────
    // Only updates payload_matrix and xml_matrix via replaceState.
    // Never touches run_sequence — that param is owned by the right-click activate action.
    function processLiveCompile() {
      var topBlocks = window.workspace.getTopBlocks(false);
      var code = ""; var found = false;
      for(var i=0;i<topBlocks.length;i++) {
        if(topBlocks[i].type==='when_sequence_activated') { found=true; code+=Blockly.Python.blockToCode(topBlocks[i]); }
      }
      if(!found) return;
      var xmlText = Blockly.Xml.domToText(Blockly.Xml.workspaceToDom(window.workspace));
      var params = new URLSearchParams(window.parent.location.search);
      params.set("payload_matrix", code);
      params.set("xml_matrix", xmlText);
      var newSearch = "?" + params.toString();
      if(window.parent.location.search !== newSearch) {
        window.parent.history.replaceState({}, '', window.parent.location.pathname + newSearch);
      }
    }
    var compileTimer = null;
    window.workspace.addChangeListener(function(e) {
      if(e.type===Blockly.Events.BLOCK_CREATE||e.type===Blockly.Events.BLOCK_MOVE||e.type===Blockly.Events.BLOCK_CHANGE||e.type===Blockly.Events.BLOCK_DELETE) {
        clearTimeout(compileTimer); compileTimer=setTimeout(processLiveCompile, 500);
      }
    });
  </script>
</body>
</html>
"""

blockly_html_payload = (
    _HTML_TEMPLATE
    .replace("%%TOOLBOX_XML%%",         blocks_registry.TOOLBOX_XML)
    .replace("%%BLOCK_DEFINITIONS_JS%%", blocks_registry.BLOCK_DEFINITIONS_JS)
    .replace("%%PYTHON_GENERATORS_JS%%", blocks_registry.PYTHON_GENERATORS_JS)
    .replace("%%SAFE_XML_STATE%%",       safe_xml_state)
    .replace("%%SAFE_TERMINAL_OUTPUT%%", safe_terminal_output)
    .replace("%%SAFE_CHAT_HISTORY%%",    safe_chat_history)
)

components.html(blockly_html_payload, height=850, scrolling=False)

st.markdown('<div class="live-code-container">', unsafe_allow_html=True)
st.subheader("📁 Live Compiled Automation Script")
st.code(st.session_state.get("synced_workspace_code", "# No code blocks assembled yet."), language="python")
st.markdown('</div>', unsafe_allow_html=True)