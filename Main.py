import os
import json
import time
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components

from dotenv import load_dotenv
from groq import Groq, RateLimitError

# Blocks folder is the single source of truth — no blocks_registry.py needed
import Blocks as BR

# ── 1. Config ─────────────────────────────────────────────────────────────────
load_dotenv()
st.set_page_config(page_title="EZHack OSINT Workspace", layout="wide")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ai_client    = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

MODEL_ROSTER = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768",
    "gemma2-9b-it",
]

def ai_reply(messages):
    if not ai_client:
        return "❌ No GROQ_API_KEY found. Add it to your .env or Streamlit secrets."
    for model in MODEL_ROSTER:
        try:
            r = ai_client.chat.completions.create(model=model, messages=messages)
            return r.choices[0].message.content
        except RateLimitError:
            st.toast(f"⚠️ Rate limit on {model}, trying next...", icon="🔄")
        except Exception as e:
            return f"❌ AI error: {str(e)}"
    return "🚨 All models rate-limited. Wait 60 seconds and try again."

# ── 2. CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp, .main, header { background-color: transparent !important; }
    .main .block-container {
        padding-top: 0 !important;
        padding-bottom: 1rem !important;
        max-width: 100% !important;
    }
    header, footer { visibility: hidden !important; height: 0 !important; }
    .live-code-box {
        margin-top: 16px; padding: 14px;
        background: #0b0f19;
        border-top: 2px solid #00ff66;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ── 3. Session state defaults ──────────────────────────────────────────────────
defaults = {
    "workspace_code":  "",
    "workspace_xml":   "",
    "terminal":        "🚀 EZHack ready. Build a sequence and right-click Activate.\n",
    "chat":            [{"role": "assistant", "content": "Hi! I'm your AI Copilot. Ask me anything about your workspace."}],
    "pending_ai_msg":  None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── 4. Handle incoming messages from the Blockly iframe ───────────────────────
#
# The iframe communicates via URL query params (Streamlit's only reliable
# cross-frame channel). Three param types:
#
#   payload_matrix  — compiled Python code from workspace (replaceState, silent)
#   xml_matrix      — workspace XML state              (replaceState, silent)
#   run_sequence    — user clicked Activate            (location.href, triggers reload)
#   ai_msg          — user sent a chat message         (location.href, triggers reload)
#
# replaceState params arrive on every render — we just sync them to session_state.
# location.href params trigger a real reload — we process them then clear them.

qp = st.query_params

if "payload_matrix" in qp:
    st.session_state["workspace_code"] = urllib.parse.unquote(qp["payload_matrix"])

if "xml_matrix" in qp:
    st.session_state["workspace_xml"] = urllib.parse.unquote(qp["xml_matrix"])

if "run_sequence" in qp and qp["run_sequence"]:
    seq_id   = urllib.parse.unquote(qp["run_sequence"])
    code     = st.session_state["workspace_code"].strip()
    st.session_state["terminal"] += f"\n🤖 Sequence [{seq_id}] activated...\n"
    if code:
        try:
            exec(code, {"run_scan": BR.run_scan, "time": time})
            st.session_state["terminal"] += "🟢 Sequence complete.\n"
        except Exception as e:
            st.session_state["terminal"] += f"💥 Error: {e}\n"
    else:
        st.session_state["terminal"] += "⚠️ No code found. Connect blocks below a SEQUENCE GENERATOR.\n"
    st.query_params.clear()
    st.rerun()

if "ai_msg" in qp and qp["ai_msg"]:
    user_text = urllib.parse.unquote(qp["ai_msg"])
    # Deduplicate — ignore if this exact message is already last in chat
    last = next((m["content"] for m in reversed(st.session_state["chat"]) if m["role"] == "user"), None)
    if user_text != last:
        st.session_state["chat"].append({"role": "user", "content": user_text})
        system_prompt = (
            "You are an AI assistant inside EZHack, a visual block-coding OSINT tool.\n"
            f"Workspace code:\n{st.session_state['workspace_code']}\n\n"
            f"Terminal output (last 800 chars):\n{st.session_state['terminal'][-800:]}\n\n"
            "Answer the user's question. Be concise and hacker-themed."
        )
        reply = ai_reply([{"role": "system", "content": system_prompt}] + st.session_state["chat"])
        st.session_state["chat"].append({"role": "assistant", "content": reply})
    st.query_params.clear()
    st.rerun()

# ── 5. Build and render the Blockly iframe ────────────────────────────────────
#
# IMPORTANT: JS is injected by string concatenation, NOT f-strings.
# JS contains many { } braces which Python f-strings would misinterpret.
# We build the HTML in named parts and join them.

safe_xml      = json.dumps(st.session_state["workspace_xml"])
safe_terminal = json.dumps(st.session_state["terminal"])
safe_chat     = json.dumps(st.session_state["chat"])

HTML_HEAD = (
    '<!DOCTYPE html><html><head><meta charset="utf-8">'
    '<script src="https://unpkg.com/blockly/blockly.min.js"></script>'
    '<script src="https://unpkg.com/blockly/python_compressed.js"></script>'
    '<script src="https://unpkg.com/blockly/blocks_compressed.js"></script>'
    '<style>'
    'html,body{height:100%;margin:0;padding:0;background:transparent;overflow:hidden;}'
    '#wrap{display:flex;flex-direction:column;height:95vh;position:relative;}'
    '#blocklyDiv{flex:1;z-index:1;position:relative;}'
    '#pCanvas{position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none;}'
    '.blocklySvg{background-color:rgba(2,4,10,0.88)!important;}'
    '.blocklyToolboxDiv{background:#0b0f19!important;border-right:2px solid #00ff66!important;}'
    '.blocklyTreeLabel{color:#fff!important;font-family:monospace!important;font-size:13px!important;font-weight:bold!important;}'
    '.blocklyTreeRow:hover{background:rgba(0,255,102,0.15)!important;}'
    '.blocklyTreeSelected .blocklyTreeRow{background:#00ff66!important;}'
    '.blocklyTreeSelected .blocklyTreeLabel{color:#000!important;}'
    '.hud{position:absolute;display:flex;flex-direction:column;background:#090d16;'
    'border:1px solid #00ff66;border-radius:8px;overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,0.8);}'
    '.hud-bar{padding:6px 10px;background:#02040a;border-bottom:1px solid #00ff66;'
    'font:bold 11px monospace;color:#00ff66;display:flex;justify-content:space-between;'
    'align-items:center;cursor:move;user-select:none;}'
    '.hud-body{flex:1;overflow-y:auto;padding:8px;}'
    '.rh{position:absolute;bottom:0;right:0;width:12px;height:12px;cursor:se-resize;'
    'background:linear-gradient(135deg,transparent 50%,#00ff66 50%);border-bottom-right-radius:6px;}'
    '.ai-theme{border-color:#00ffcc!important;}'
    '.ai-theme .hud-bar{border-color:#00ffcc!important;color:#00ffcc!important;}'
    '.ai-theme .rh{background:linear-gradient(135deg,transparent 50%,#00ffcc 50%)!important;}'
    '#aiRow{padding:6px;background:#02040a;border-top:1px solid #00ffcc;display:flex;gap:5px;}'
    '#aiInp{flex:1;background:#05070f;border:1px solid #00ffcc;color:#00ffcc;'
    'padding:5px;border-radius:3px;font:11px monospace;}'
    '#aiInp:focus{outline:none;}'
    '#aiBtn{background:#02040a;color:#00ffcc;border:1px solid #00ffcc;padding:4px 10px;'
    'cursor:pointer;border-radius:3px;font:bold 11px monospace;}'
    '#aiBtn:hover{background:#00ffcc;color:#02040a;}'
    '</style></head><body>'
    '<div id="wrap">'
    '<canvas id="pCanvas"></canvas>'
    '<div id="blocklyDiv"></div>'
    '</div>'
)

HTML_AFTER_TOOLBOX = (
    '<script>'
    # ── Particles ──
    'var pc=document.getElementById("pCanvas"),px=pc.getContext("2d"),pw,ph,pts=[],mo={x:null,y:null};'
    'function rz(){pw=window.innerWidth;ph=window.innerHeight;pc.width=pw;pc.height=ph;}'
    'window.addEventListener("resize",rz);rz();'
    'window.addEventListener("mousemove",function(e){mo.x=e.clientX;mo.y=e.clientY;});'
    'for(var i=0;i<50;i++)pts.push({x:Math.random()*1200,y:Math.random()*700,vx:(Math.random()-.5)*1.5,vy:(Math.random()-.5)*1.5});'
    'function ap(){'
    'px.clearRect(0,0,pw,ph);'
    'pts.forEach(function(p){'
    'p.x+=p.vx;p.y+=p.vy;'
    'if(p.x<0||p.x>pw)p.vx*=-1;if(p.y<0||p.y>ph)p.vy*=-1;'
    'px.beginPath();px.arc(p.x,p.y,1.5,0,Math.PI*2);px.fillStyle="rgba(0,255,102,.7)";px.fill();'
    'if(mo.x!=null){var dx=mo.x-p.x,dy=mo.y-p.y,d=Math.sqrt(dx*dx+dy*dy);'
    'if(d<160){px.beginPath();px.strokeStyle="rgba(0,255,102,"+(1-d/160)+")";px.lineWidth=1;px.moveTo(p.x,p.y);px.lineTo(mo.x,mo.y);px.stroke();}}'
    'pts.forEach(function(q){var dx=p.x-q.x,dy=p.y-q.y,d=Math.sqrt(dx*dx+dy*dy);'
    'if(d<100){px.beginPath();px.strokeStyle="rgba(0,255,102,"+(0.15-d/700)+")";px.lineWidth=.5;px.moveTo(p.x,p.y);px.lineTo(q.x,q.y);px.stroke();}});'
    '});requestAnimationFrame(ap);}'
    'ap();'
)

HTML_AFTER_JS = (
    # ── Blockly init ──
    'window.ws=Blockly.inject("blocklyDiv",{'
    'toolbox:document.getElementById("toolbox"),'
    'grid:{spacing:40,length:40,colour:"rgba(0,255,102,0.15)",snap:true},'
    'move:{scrollbars:true,drag:true,wheel:true},'
    'zoom:{controls:true,wheel:true,startScale:1.0,maxScale:3,minScale:0.3,scaleSpeed:1.2},'
    'trashcan:true});'
    'window.workspace=window.ws;' # alias so block definitions can use either name
    # ── Restore XML ──
    'try{'
    'var sx=' + safe_xml + ';'
    'if(sx&&sx.trim()!==""){Blockly.Xml.domToWorkspace(Blockly.utils.xml.textToDom(sx),window.ws);}'
    '}catch(e){console.error("XML restore:",e);}'
    # ── Terminal HUD ──
    'var sv=window.ws.getCanvas();'
    'var tfo=document.createElementNS("http://www.w3.org/2000/svg","foreignObject");'
    'tfo.setAttribute("x","20");tfo.setAttribute("y","20");'
    'tfo.setAttribute("width","400");tfo.setAttribute("height","260");'
    'var td=document.createElement("div");td.style.cssText="width:100%;height:100%;";'
    'td.innerHTML='
    '"<div class=\\"hud\\" style=\\"width:100%;height:100%;\\"><div class=\\"hud-bar\\" id=\\"th\\">&#x1F4BB; TERMINAL<span style=\\"font-size:9px;color:#556\\">[drag]</span></div>'
    '<div class=\\"hud-body\\"><pre id=\\"tlog\\" style=\\"margin:0;color:#00ff66;font-size:11px;line-height:1.5;white-space:pre-wrap;\\"></pre></div>'
    '<div class=\\"rh\\" id=\\"trh\\"></div></div>";'
    'tfo.appendChild(td);sv.appendChild(tfo);'
    '["mousedown","pointerdown","keydown"].forEach(function(e){td.addEventListener(e,function(v){v.stopPropagation();});});'
    'document.getElementById("tlog").textContent=' + safe_terminal + ';'
    'document.getElementById("tlog").parentElement.scrollTop=999999;'
    # ── AI HUD ──
    'var afo=document.createElementNS("http://www.w3.org/2000/svg","foreignObject");'
    'afo.setAttribute("x","440");afo.setAttribute("y","20");'
    'afo.setAttribute("width","380");afo.setAttribute("height","500");'
    'var ad=document.createElement("div");ad.style.cssText="width:100%;height:100%;";'
    'ad.innerHTML='
    '"<div class=\\"hud ai-theme\\" style=\\"width:100%;height:100%;\\"><div class=\\"hud-bar\\" id=\\"ah\\">&#x1F916; AI CO-PILOT<span style=\\"font-size:9px;color:#556\\">[drag]</span></div>'
    '<div class=\\"hud-body\\" id=\\"achat\\"></div>'
    '<div id=\\"aiRow\\"><input type=\\"text\\" id=\\"aiInp\\" placeholder=\\"Ask the AI Copilot...\\" autocomplete=\\"off\\"><button id=\\"aiBtn\\">SEND</button></div>'
    '<div class=\\"rh\\" id=\\"arh\\"></div></div>";'
    'afo.appendChild(ad);sv.appendChild(afo);'
    '["mousedown","pointerdown","keydown"].forEach(function(e){ad.addEventListener(e,function(v){v.stopPropagation();});});'
    # ── Render chat ──
    'var ch=' + safe_chat + ';'
    'function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\\n/g,"<br>");}'
    'function rc(){'
    'var c=document.getElementById("achat");c.innerHTML="";'
    'ch.forEach(function(m){'
    'var d=document.createElement("div");'
    'd.style.cssText="margin-bottom:9px;padding:6px 9px;border-radius:4px;font:11px monospace;line-height:1.5;word-break:break-word;";'
    'if(m.role==="user"){'
    'd.style.background="#02040a";d.style.color="#00ffcc";d.style.borderRight="2px solid #00ffcc";'
    'd.innerHTML="<div style=\\"font-size:9px;color:#556;margin-bottom:2px;\\">YOU:</div>"+esc(m.content);'
    '}else{'
    'd.style.background="#05070f";d.style.color="#e0e0e0";d.style.borderLeft="2px solid #00ffcc";'
    'd.innerHTML="<div style=\\"font-size:9px;color:#00ffcc;margin-bottom:2px;\\">AI:</div>"+esc(m.content);'
    '}'
    'c.appendChild(d);});'
    'c.scrollTop=c.scrollHeight;}'
    'rc();'
    # ── AI send ──
    'function send(){'
    'var inp=document.getElementById("aiInp");'
    'var txt=inp.value.trim();if(!txt)return;'
    'inp.value="";inp.disabled=true;document.getElementById("aiBtn").textContent="...";'
    'ch.push({role:"user",content:txt});rc();'
    'var code="";'
    'window.ws.getTopBlocks(false).forEach(function(b){'
    'if(b.type==="when_sequence_activated")code+=Blockly.Python.blockToCode(b);});'
    'var xml=Blockly.Xml.domToText(Blockly.Xml.workspaceToDom(window.ws));'
    'var base=window.parent.location.origin+window.parent.location.pathname;'
    'window.parent.location.href=base'
    '+"?payload_matrix="+encodeURIComponent(code)'
    '+"&xml_matrix="+encodeURIComponent(xml)'
    '+"&ai_msg="+encodeURIComponent(txt);}'
    'document.getElementById("aiBtn").addEventListener("click",send);'
    'document.getElementById("aiInp").addEventListener("keydown",function(e){if(e.key==="Enter")send();});'
    # ── Drag ──
    'function mkDrag(id,fo){'
    'var dr=false,sx=0,sy=0;'
    'document.getElementById(id).addEventListener("mousedown",function(e){'
    'dr=true;var sc=window.ws.scale||1;'
    'sx=e.clientX/sc-parseFloat(fo.getAttribute("x"));'
    'sy=e.clientY/sc-parseFloat(fo.getAttribute("y"));'
    'e.stopPropagation();e.preventDefault();});'
    'document.addEventListener("mousemove",function(e){'
    'if(!dr)return;var sc=window.ws.scale||1;'
    'fo.setAttribute("x",e.clientX/sc-sx);fo.setAttribute("y",e.clientY/sc-sy);});'
    'document.addEventListener("mouseup",function(){dr=false;});}'
    # ── Resize ──
    'function mkRes(id,fo,mw,mh){'
    'var rs=false,sw=0,sh=0,rx=0,ry=0;'
    'document.getElementById(id).addEventListener("mousedown",function(e){'
    'rs=true;var sc=window.ws.scale||1;'
    'sw=parseFloat(fo.getAttribute("width"));sh=parseFloat(fo.getAttribute("height"));'
    'rx=e.clientX/sc;ry=e.clientY/sc;e.stopPropagation();e.preventDefault();});'
    'document.addEventListener("mousemove",function(e){'
    'if(!rs)return;var sc=window.ws.scale||1;'
    'var nw=sw+(e.clientX/sc-rx),nh=sh+(e.clientY/sc-ry);'
    'if(nw>mw)fo.setAttribute("width",nw);if(nh>mh)fo.setAttribute("height",nh);});'
    'document.addEventListener("mouseup",function(){rs=false;});}'
    'mkDrag("th",tfo);mkRes("trh",tfo,180,120);'
    'mkDrag("ah",afo);mkRes("arh",afo,180,180);'
    # ── Live compile: uses location.href so Streamlit reruns and sees new code ──
    # Fires 2 seconds after the user stops editing (debounced).
    # Skips reload if code hasn't changed since last sync.
    'var lastSyncedCode="";var ct=null;'
    'function lc(){'
    'var code="",found=false;'
    'window.ws.getTopBlocks(false).forEach(function(b){'
    'if(b.type==="when_sequence_activated"){found=true;code+=Blockly.Python.blockToCode(b);}});'
    'if(!found||code===lastSyncedCode)return;'
    'lastSyncedCode=code;'
    'var xml=Blockly.Xml.domToText(Blockly.Xml.workspaceToDom(window.ws));'
    'var base=window.parent.location.origin+window.parent.location.pathname;'
    'window.parent.location.href=base+"?payload_matrix="+encodeURIComponent(code)+"&xml_matrix="+encodeURIComponent(xml);}'
    'window.ws.addChangeListener(function(e){'
    'if([Blockly.Events.BLOCK_CREATE,Blockly.Events.BLOCK_MOVE,'
    'Blockly.Events.BLOCK_CHANGE,Blockly.Events.BLOCK_DELETE].indexOf(e.type)>=0){'
    'clearTimeout(ct);ct=setTimeout(lc,2000);}});'
    '</script></body></html>'
)

blockly_html = (
    HTML_HEAD
    + BR.TOOLBOX_XML
    + HTML_AFTER_TOOLBOX
    + BR.BLOCK_DEFINITIONS_JS
    + BR.PYTHON_GENERATORS_JS
    + HTML_AFTER_JS
)

components.html(blockly_html, height=850, scrolling=False)

# ── 6. Live code display ───────────────────────────────────────────────────────
st.markdown('<div class="live-code-box">', unsafe_allow_html=True)
st.subheader("📁 Live Compiled Automation Script")
st.code(st.session_state["workspace_code"] or "# No blocks connected yet.", language="python")
st.markdown('</div>', unsafe_allow_html=True)