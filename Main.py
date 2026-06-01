import os
import json
import urllib.parse
import time
import streamlit as st
import streamlit.components.v1 as components

from dotenv import load_dotenv
from groq import Groq, RateLimitError

# Import our separated block module payloads
import block_registry as blocks_registry

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
try:
    rerun_required = False

    if "payload_matrix" in st.query_params:
        st.session_state["synced_workspace_code"] = urllib.parse.unquote(st.query_params["payload_matrix"])
        
    if "xml_matrix" in st.query_params:
        st.session_state["blockly_xml_state"] = urllib.parse.unquote(st.query_params["xml_matrix"])
        
    if "ai_msg" in st.query_params and st.query_params["ai_msg"]:
        user_text = urllib.parse.unquote(st.query_params["ai_msg"])
        del st.query_params["ai_msg"]
        st.session_state["chat_messages"].append({"role": "user", "content": user_text})
        
        if ai_client:
            system_context = f"""
            You are an elite pentesting AI assistant embedded in a visual block-coding platform.
            The user is building security and OSINT tools by dragging logic blocks.
            
            Current compiled workspace Python code:
            {st.session_state.get("synced_workspace_code", "")}
            
            Current output console logs:
            {st.session_state.get("terminal_history_output", "")}
            
            Analyze the user's workspace, explain what their blocks are doing, and answer their prompt.
            Keep it hacker-themed, concise, and educational. Do not generate destructive payloads.
            """
            api_messages = [{"role": "system", "content": system_context}] + st.session_state["chat_messages"]
            reply = generate_completion_with_fallback(api_messages)
            st.session_state["chat_messages"].append({"role": "assistant", "content": reply})
        rerun_required = True

    if "run_sequence" in st.query_params and st.query_params["run_sequence"]:
        sequence_id_name = urllib.parse.unquote(st.query_params["run_sequence"])
        del st.query_params["run_sequence"]
        
        st.session_state["terminal_history_output"] += f"\n🤖 Booting sequence pipeline [{sequence_id_name}]...\nRunning target compiled script layers...\n"
        code_to_run = st.session_state["synced_workspace_code"].strip()
        if code_to_run:
            try:
                exec_scope = {"run_scan": blocks_registry.run_scan, "time": time}
                exec(code_to_run, exec_scope)
                st.session_state["terminal_history_output"] += "\n🟢 Execution automation run complete!"
            except Exception as runtime_err:
                st.session_state["terminal_history_output"] += f"\n💥 PIPELINE BREAK: {str(runtime_err)}"
        rerun_required = True

    if rerun_required:
        st.rerun()
except Exception:
    pass

safe_xml_state = json.dumps(st.session_state.get("blockly_xml_state", ""))
safe_terminal_output = json.dumps(st.session_state.get("terminal_history_output", ""))
safe_chat_history = json.dumps(st.session_state.get("chat_messages", []))

# --- 4. Render Dynamic SVG HTML Components ---
blockly_html_payload = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://unpkg.com/blockly/blockly.min.js"></script>
  <script src="https://unpkg.com/blockly/python_compressed.js"></script>
  <script src="https://unpkg.com/blockly/blocks_compressed.js"></script>
  <style>
    html, body {{ height: 100%; width: 100%; margin: 0; padding: 0; background-color: transparent; overflow: hidden; }}
    ::-webkit-scrollbar {{ display: none; }}
    
    #workspaceWrapper {{ position: absolute; top: 0; left: 0; width: 100vw; height: 100vh; display: flex; flex-direction: column; padding: 0; box-sizing: border-box; }}
    #blocklyDiv {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }}
    
    #particle-canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 0; background-color: transparent; }}
    .blocklySvg {{ background-color: rgba(2, 4, 10, 0.85) !important; }}
    
    body .blocklyToolboxDiv {{
        background-color: #0b0f19 !important;
        border-right: 2px solid #00ff66 !important;
        -webkit-user-select: none !important;
        user-select: none !important;
    }}
    body .blocklyTreeRow {{
        background-color: #0b0f19 !important;
        border-radius: 4px !important;
        transition: background-color 0.1s;
    }}
    body .blocklyTreeLabel {{
        color: #ffffff !important;
        font-family: monospace !important;
        font-size: 14px !important;
        font-weight: bold !important;
        padding: 5px !important;
    }}
    body .blocklyTreeRow:hover {{
        background-color: rgba(0, 255, 102, 0.2) !important;
    }}
    body .blocklyTreeSelected .blocklyTreeRow {{
        background-color: #00ff66 !important;
    }}
    body .blocklyTreeSelected .blocklyTreeLabel {{
        color: #000000 !important;
    }}
    .blocklyFlyout {{ overflow: visible !important; z-index: 9999 !important; }}
    .blocklyFlyoutBackground {{ fill: #0b0f19 !important; fill-opacity: 0.95 !important; border-right: 1px solid #00ff66; }}
    
    .hud-window {{ display: flex; flex-direction: column; height: 100%; background-color: #090d16; border: 1px solid #00ff66; border-radius: 8px; box-shadow: 0 10px 40px rgba(0,0,0,0.8); overflow: hidden; position: relative; }}
    .hud-header {{ padding: 8px 12px; cursor: move; background-color: #02040a; border-bottom: 1px solid #00ff66; font-weight: bold; color: #00ff66; font-size: 11px; display: flex; justify-content: space-between; align-items: center; user-select: none; }}
    .hud-body {{ flex: 1; padding: 10px; background-color: #05070f; overflow-y: auto; font-size: 11px; font-family: monospace; line-height: 1.4; }}
    .resize-handle {{ position: absolute; bottom: 0; right: 0; width: 14px; height: 14px; cursor: se-resize; background: linear-gradient(135deg, transparent 50%, #00ff66 50%); border-bottom-right-radius: 6px; z-index: 100; }}
    
    .ai-theme {{ border-color: #00ffcc; }}
    .ai-theme .hud-header {{ border-color: #00ffcc; color: #00ffcc; }}
    .ai-theme .resize-handle {{ background: linear-gradient(135deg, transparent 50%, #00ffcc 50%); }}
    #aiTabInputArea {{ padding: 6px; background-color: #02040a; border-top: 1px solid #00ffcc; display: flex; gap: 6px; }}
    #aiTabInputField {{ flex: 1; background-color: #05070f; border: 1px solid #00ffcc; color: #00ffcc; padding: 6px; border-radius: 4px; font-family: monospace; font-size: 11px; }}
    #aiTabInputField:focus {{ outline: none; border-color: #1fec79; }}
    #aiTabSendBtn {{ background: #02040a; color: #00ffcc; border: 1px solid #00ffcc; padding: 4px 10px; cursor: pointer; border-radius: 4px; font-family: monospace; font-size: 11px; font-weight: bold; }}
    #aiTabSendBtn:hover {{ background: #00ffcc; color: #02040a; }}
  </style>
</head>
<body>

  <div id="workspaceWrapper">
    <canvas id="particle-canvas"></canvas>
    <div id="blocklyDiv"></div>
  </div>

  {blocks_registry.TOOLBOX_XML}

  <script>
    const canvasEl = document.getElementById('particle-canvas');
    const ctx = canvasEl.getContext('2d');
    let width, height;
    let particles = [];
    const mouse = {{ x: null, y: null }};

    function resizeCanvas() {{
        width = window.innerWidth;
        height = window.innerHeight;
        canvasEl.width = width;
        canvasEl.height = height;
    }}
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    window.addEventListener('mousemove', (e) => {{
        mouse.x = e.clientX;
        mouse.y = e.clientY;
    }});

    class Particle {{
        constructor() {{
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * 1.5;
            this.vy = (Math.random() - 0.5) * 1.5;
        }}
        update() {{
            this.x += this.vx;
            this.y += this.vy;
            if (this.x < 0 || this.x > width) this.vx *= -1;
            if (this.y < 0 || this.y > height) this.vy *= -1;
        }}
        draw() {{
            ctx.beginPath();
            ctx.arc(this.x, this.y, 1.5, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(0, 255, 102, 0.8)';
            ctx.fill();
        }}
    }}

    for(let i = 0; i < 90; i++) particles.push(new Particle());

    function animateParticles() {{
        ctx.clearRect(0, 0, width, height);
        
        particles.forEach(p => {{
            p.update();
            p.draw();
            if (mouse.x != null) {{
                let dx = mouse.x - p.x;
                let dy = mouse.y - p.y;
                let dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < 180) {{
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(0, 255, 102, ${{1 - dist/180}})`;
                    ctx.lineWidth = 1;
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(mouse.x, mouse.y);
                    ctx.stroke();
                }}
            }}
            particles.forEach(p2 => {{
                let dx = p.x - p2.x;
                let dy = p.y - p2.y;
                let dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < 120) {{
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(0, 255, 102, ${{0.2 - dist/600}})`;
                    ctx.lineWidth = 0.5;
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }}
            }});
        }});
        requestAnimationFrame(animateParticles);
    }}
    animateParticles();

    {blocks_registry.BLOCK_DEFINITIONS_JS}
    {blocks_registry.PYTHON_GENERATORS_JS}

    window.workspace = Blockly.inject('blocklyDiv', {{
      toolbox: document.getElementById('toolbox'),
      grid: {{ spacing: 40, length: 40, colour: 'rgba(0, 255, 102, 0.2)', snap: true }}, 
      move: {{ scrollbars: true, drag: true, wheel: true }},
      zoom: {{ controls: true, wheel: true, startScale: 1.0, maxScale: 3, minScale: 0.3, scaleSpeed: 1.2 }},
      trashcan: true
    }});
    
    // THE ULTIMATE FIX: Disable transition animations and bind directly to click captures
    document.addEventListener("DOMContentLoaded", function() {{
        setTimeout(function() {{
            var toolboxContainer = document.querySelector('.blocklyToolboxDiv');
            if (toolboxContainer) {{
                toolboxContainer.addEventListener('click', function(e) {{
                    // Intercept immediate changes and force an explicit layout evaluation loop
                    for(let offset of [0, 50, 150, 300]) {{
                        setTimeout(function() {{
                            if (window.workspace) {{
                                Blockly.svgResize(window.workspace);
                                var flyout = window.workspace.getFlyout();
                                if (flyout) {{
                                    if (flyout.isVisible()) {{
                                        flyout.reflow();
                                        // Re-render blocks inside the flyout directly
                                        if(flyout.workspace_) {{
                                            Blockly.svgResize(flyout.workspace_);
                                        }}
                                    }}
                                }}
                            }}
                        }}, offset);
                    }}
                }}, true);
            }}
        }}, 500);
    }});
    
    try {{
      var initialXmlText = {safe_xml_state};
      if (initialXmlText && initialXmlText.trim() !== "") {{
        var dom = Blockly.utils.xml.textToDom(initialXmlText);
        Blockly.Xml.domToWorkspace(dom, window.workspace);
      }}
    }} catch (err) {{
      console.error("Hydration Layer Failure:", err);
    }}

    var canvas = window.workspace.getCanvas();

    var termForeignObject = document.createElementNS("http://www.w3.org/2000/svg", "foreignObject");
    termForeignObject.setAttribute("x", "40"); termForeignObject.setAttribute("y", "40");
    termForeignObject.setAttribute("width", "420"); termForeignObject.setAttribute("height", "280");
    var termTabDiv = document.createElement("div"); termTabDiv.style.width = "100%"; termTabDiv.style.height = "100%";
    termTabDiv.innerHTML = `
      <div id="terminalWindow" class="hud-window">
        <div id="terminalHeader" class="hud-header">
          <span>💻 SYSTEM TERMINAL OUTPUT</span><span style="font-size:9px; color:#888;">[DRAGGABLE WORKSPACE TAB]</span>
        </div>
        <div class="hud-body"><pre id="terminalLogOutput" style="margin: 0; color: #00ff66; font-size: 12px; line-height: 1.4; white-space: pre-wrap; font-family: monospace;"></pre></div>
        <div class="resize-handle" id="terminalResizeAnchor"></div>
      </div>
    `;
    termForeignObject.appendChild(termTabDiv); canvas.appendChild(termForeignObject);
    termTabDiv.addEventListener("mousedown", function(e) {{ e.stopPropagation(); }});
    termTabDiv.addEventListener("pointerdown", function(e) {{ e.stopPropagation(); }});
    termTabDiv.addEventListener("keydown", function(e) {{ e.stopPropagation(); }});

    var termLogOutput = document.getElementById("terminalLogOutput");
    termLogOutput.textContent = {safe_terminal_output};
    termLogOutput.parentElement.scrollTop = termLogOutput.parentElement.scrollHeight;

    var aiForeignObject = document.createElementNS("http://www.w3.org/2000/svg", "foreignObject");
    aiForeignObject.setAttribute("x", "480"); aiForeignObject.setAttribute("y", "40");
    aiForeignObject.setAttribute("width", "390"); aiForeignObject.setAttribute("height", "520");
    var aiTabDiv = document.createElement("div"); aiTabDiv.style.width = "100%"; aiTabDiv.style.height = "100%";
    aiTabDiv.innerHTML = `
      <div id="aiTabWindow" class="hud-window ai-theme">
        <div id="aiTabHeader" class="hud-header">
          <span>🤖 AI CO-PILOT MATRIX</span><span style="font-size:9px; color:#888;">[DRAGGABLE WORKSPACE TAB]</span>
        </div>
        <div class="hud-body" id="aiTabChatContent"></div>
        <div id="aiTabInputArea">
          <input type="text" id="aiTabInputField" placeholder="Ask AI Copilot or type logic prompt..." autocomplete="off">
          <button id="aiTabSendBtn">SEND</button>
        </div>
        <div class="resize-handle" id="aiTabResizeHandle"></div>
      </div>
    `;
    aiForeignObject.appendChild(aiTabDiv); canvas.appendChild(aiForeignObject);
    aiTabDiv.addEventListener("mousedown", function(e) {{ e.stopPropagation(); }});
    aiTabDiv.addEventListener("pointerdown", function(e) {{ e.stopPropagation(); }});
    aiTabDiv.addEventListener("keydown", function(e) {{ e.stopPropagation(); }});
    
    var chatHistory = {safe_chat_history};
    function renderChatHistory() {{
      var container = document.getElementById("aiTabChatContent"); container.innerHTML = "";
      chatHistory.forEach(function(msg) {{
        var msgDiv = document.createElement("div"); msgDiv.style.marginBottom = "10px"; msgDiv.style.padding = "6px 10px"; msgDiv.style.borderRadius = "4px"; msgDiv.style.wordBreak = "break-word";
        if (msg.role === "user") {{
          msgDiv.style.backgroundColor = "#02040a"; msgDiv.style.color = "#00ffcc"; msgDiv.style.borderRight = "2px solid #00ffcc"; msgDiv.innerHTML = "<div style='font-weight:bold;font-size:9px;color:#888;margin-bottom:2px;'>OPERATOR:</div>" + escapeHtml(msg.content);
        }} else if (msg.role === "assistant") {{
          msgDiv.style.backgroundColor = "#05070f"; msgDiv.style.color = "#ffffff"; msgDiv.style.borderLeft = "2px solid #00ffcc"; msgDiv.innerHTML = "<div style='font-weight:bold;font-size:9px;color:#00ffcc;margin-bottom:2px;'>GROQ CORERUN:</div>" + escapeHtml(msg.content);
        }}
        container.appendChild(msgDiv);
      }});
      container.scrollTop = container.scrollHeight;
    }}
    
    function escapeHtml(str) {{ return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;").replace(/\\n/g, "<br>"); }}
    renderChatHistory();
    
    function handleTabSend() {{
      var inputField = document.getElementById("aiTabInputField"); var text = inputField.value.trim();
      if(!text) return; inputField.value = "";
      var topBlocks = window.workspace.getTopBlocks(false); var generatedPythonCode = "";
      for (var i = 0; i < topBlocks.length; i++) {{ if (topBlocks[i].type === 'when_sequence_activated') {{ generatedPythonCode += Blockly.Python.blockToCode(topBlocks[i]); }} }}
      var xmlDom = Blockly.Xml.workspaceToDom(window.workspace); var currentXmlText = Blockly.Xml.domToText(xmlDom);
      var baseUrl = window.parent.location.origin + window.parent.location.pathname;
      var targetUrl = baseUrl + "?payload_matrix=" + encodeURIComponent(generatedPythonCode) + "&xml_matrix=" + encodeURIComponent(currentXmlText) + "&ai_msg=" + encodeURIComponent(text);
      window.parent.location.href = targetUrl;
    }}
    document.getElementById("aiTabSendBtn").onclick = handleTabSend;
    document.getElementById("aiTabInputField").onkeydown = function(e) {{ if(e.key === "Enter") {{ handleTabSend(); }} }};

    var isDraggingTerm = false, termStartX, termStartY, isResizingTerm = false, termStartW, termStartH, termResStartX, termResStartY;
    document.getElementById("terminalHeader").onmousedown = function(e) {{ isDraggingTerm = true; var scale = window.workspace.scale || 1; termStartX = e.clientX / scale - parseFloat(termForeignObject.getAttribute("x")); termStartY = e.clientY / scale - parseFloat(termForeignObject.getAttribute("y")); e.stopPropagation(); e.preventDefault(); }};
    document.getElementById("terminalResizeAnchor").onmousedown = function(e) {{ isResizingTerm = true; var scale = window.workspace.scale || 1; termStartW = parseFloat(termForeignObject.getAttribute("width")); termStartH = parseFloat(termForeignObject.getAttribute("height")); termResStartX = e.clientX / scale; termResStartY = e.clientY / scale; e.stopPropagation(); e.preventDefault(); }};

    var isDraggingAI = false, aiStartX, aiStartY, isResizingAI = false, aiStartW, aiStartH, aiResStartX, aiResStartY;
    document.getElementById("aiTabHeader").onmousedown = function(e) {{ isDraggingAI = true; var scale = window.workspace.scale || 1; aiStartX = e.clientX / scale - parseFloat(aiForeignObject.getAttribute("x")); aiStartY = e.clientY / scale - parseFloat(aiForeignObject.getAttribute("y")); e.stopPropagation(); e.preventDefault(); }};
    document.getElementById("aiTabResizeHandle").onmousedown = function(e) {{ isResizingAI = true; var scale = window.workspace.scale || 1; aiStartW = parseFloat(aiForeignObject.getAttribute("width")); aiStartH = parseFloat(aiForeignObject.getAttribute("height")); aiResStartX = e.clientX / scale; aiResStartY = e.clientY / scale; e.stopPropagation(); e.preventDefault(); }};

    document.addEventListener("mousemove", function(e) {{
      var scale = window.workspace.scale || 1;
      if (isDraggingTerm) {{ termForeignObject.setAttribute("x", e.clientX / scale - termStartX); termForeignObject.setAttribute("y", e.clientY / scale - termStartY); }}
      if (isResizingTerm) {{ var newWT = termStartW + (e.clientX / scale - termResStartX); var newHT = termStartH + (e.clientY / scale - termResStartY); if (newWT > 200) termForeignObject.setAttribute("width", newWT); if (newHT > 150) termForeignObject.setAttribute("height", newHT); }}
      if (isDraggingAI) {{ aiForeignObject.setAttribute("x", e.clientX / scale - aiStartX); aiForeignObject.setAttribute("y", e.clientY / scale - aiStartY); }}
      if (isResizingAI) {{ var newWA = aiStartW + (e.clientX / scale - aiResStartX); var newHA = aiStartH + (e.clientY / scale - aiResStartY); if (newWA > 200) aiForeignObject.setAttribute("width", newWA); if (newHA > 200) aiForeignObject.setAttribute("height", newHA); }}
    }});
    
    document.addEventListener("mouseup", function() {{ isDraggingTerm = false; isResizingTerm = false; isDraggingAI = false; isResizingAI = false; }});

    function processLiveDebugCompilations() {{
      var topBlocks = window.workspace.getTopBlocks(false); var generatedPythonCode = ""; var sequenceFound = false;
      for (var i = 0; i < topBlocks.length; i++) {{ if (topBlocks[i].type === 'when_sequence_activated') {{ sequenceFound = true; generatedPythonCode += Blockly.Python.blockToCode(topBlocks[i]); }} }}
      var xmlDom = Blockly.Xml.workspaceToDom(window.workspace); var currentXmlText = Blockly.Xml.domToText(xmlDom);
      if(sequenceFound) {{
        var targetUrl = window.parent.location.origin + window.parent.location.pathname + "?payload_matrix=" + encodeURIComponent(generatedPythonCode) + "&xml_matrix=" + encodeURIComponent(currentXmlText);
        if(window.parent.location.search !== "?payload_matrix=" + encodeURIComponent(generatedPythonCode) + "&xml_matrix=" + encodeURIComponent(currentXmlText)) {{ window.parent.history.replaceState({{}}, '', targetUrl); }}
      }}
    }}

    var compileTimeout = null;
    window.workspace.addChangeListener(function(e) {{
      if (e.type === Blockly.Events.BLOCK_CREATE || e.type === Blockly.Events.BLOCK_MOVE || e.type === Blockly.Events.BLOCK_CHANGE || e.type === Blockly.Events.BLOCK_DELETE) {{
        clearTimeout(compileTimeout); compileTimeout = setTimeout(processLiveDebugCompilations, 500);
      }}
    }});
  </script>
</body>
</html>
"""

components.html(blockly_html_payload, height=850, scrolling=False)

st.markdown('<div class="live-code-container">', unsafe_allow_html=True)
st.subheader("📁 Live Compiled Automation Script")
st.code(st.session_state.get("synced_workspace_code", "# No code blocks assembled yet."), language="python")
st.markdown('</div>', unsafe_allow_html=True)