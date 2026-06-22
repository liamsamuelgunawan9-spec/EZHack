import os
import json
import time
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components

from dotenv import load_dotenv
from groq import Groq, RateLimitError

import Blocks as BR

# â”€â”€ 1. Config â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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
        return "âŒ No GROQ_API_KEY found."
    for model in MODEL_ROSTER:
        try:
            r = ai_client.chat.completions.create(model=model, messages=messages)
            return r.choices[0].message.content
        except RateLimitError:
            st.toast(f"âš ï¸ Rate limit on {model}, trying next...", icon="ðŸ”„")
        except Exception as e:
            return f"âŒ AI error: {str(e)}"
    return "ðŸš¨ All models rate-limited. Wait 60 seconds."

# â”€â”€ 2. CSS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.markdown("""
<style>
    .stApp, .main, header { background-color: transparent !important; }
    .main .block-container { padding-top:0!important; padding-bottom:1rem!important; max-width:100%!important; }
    header, footer { visibility:hidden!important; height:0!important; }
    .live-code-box { margin-top:16px; padding:14px; background:#0b0f19; border-top:2px solid #00ff66; border-radius:8px; }
</style>
""", unsafe_allow_html=True)

# â”€â”€ 3. Session state â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
defaults = {
    "workspace_code": "",
    "workspace_xml":  "",
    "terminal":       "ðŸš€ EZHack ready.\n",
    "chat":           [{"role": "assistant", "content": "Hi! I'm your AI Copilot."}],
    "last_component_nonce": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# â”€â”€ 4. Query param handling â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
qp = st.query_params

if "payload_matrix" in qp:
    st.session_state["workspace_code"] = urllib.parse.unquote(qp["payload_matrix"])

if "xml_matrix" in qp:
    st.session_state["workspace_xml"] = urllib.parse.unquote(qp["xml_matrix"])

if "run_sequence" in qp and qp["run_sequence"]:
    seq_id = urllib.parse.unquote(qp["run_sequence"])
    code   = st.session_state["workspace_code"].strip()
    st.session_state["terminal"] += f"\nðŸ¤– Sequence [{seq_id}] activated...\n"
    if code:
        try:
            exec(code, {"run_scan": BR.run_scan, "time": time})
            st.session_state["terminal"] += "ðŸŸ¢ Sequence complete.\n"
        except Exception as e:
            st.session_state["terminal"] += f"ðŸ’¥ Error: {e}\n"
    else:
        st.session_state["terminal"] += "âš ï¸ No code found. Connect blocks below a SEQUENCE GENERATOR.\n"
    st.query_params.clear()
    st.rerun()

if "ai_msg" in qp and qp["ai_msg"]:
    user_text = urllib.parse.unquote(qp["ai_msg"])
    last = next((m["content"] for m in reversed(st.session_state["chat"]) if m["role"] == "user"), None)
    if user_text != last:
        st.session_state["chat"].append({"role": "user", "content": user_text})
        system_prompt = (
            "You are an AI assistant inside EZHack, a visual block-coding OSINT tool.\n"
            f"Workspace code:\n{st.session_state['workspace_code']}\n\n"
            f"Terminal output:\n{st.session_state['terminal'][-800:]}\n\n"
            "Be concise and hacker-themed."
        )
        reply = ai_reply([{"role": "system", "content": system_prompt}] + st.session_state["chat"])
        st.session_state["chat"].append({"role": "assistant", "content": reply})
    st.query_params.clear()
    st.rerun()

# â”€â”€ 5. Build Blockly HTML â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Rules:
#   - Never use f-strings for JS (curly braces get misinterpreted)
#   - Never use \\\" for innerHTML (becomes \" in browser = JS syntax error)
#   - Use single quotes inside JS strings so no escaping needed at all
#   - Inject dynamic Python values via direct string concatenation only

safe_xml      = json.dumps(st.session_state["workspace_xml"])
safe_terminal = json.dumps(st.session_state["terminal"])
safe_chat     = json.dumps(st.session_state["chat"])

# â”€â”€ HEAD + CSS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
H = (
'<!DOCTYPE html><html><head><meta charset="utf-8">'
'<script src="https://unpkg.com/blockly/blockly.min.js"></script>'
'<script src="https://unpkg.com/blockly/python_compressed.js"></script>'
'<script src="https://unpkg.com/blockly/blocks_compressed.js"></script>'
'<style>'
'*{box-sizing:border-box}'
'html,body{height:100%;margin:0;padding:0;background:#02040a;overflow:hidden;font-family:monospace}'
'#wrap{display:flex;flex-direction:column;height:100vh;position:relative}'
'#pCanvas{position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none}'
'#blocklyDiv{flex:1;z-index:1;position:relative}'
'.blocklySvg{background-color:rgba(2,4,10,0.9)!important}'
'.blocklyToolboxDiv{background:#0b0f19!important;border-right:2px solid #00ff66!important}'
'.blocklyTreeLabel{color:#fff!important;font-family:monospace!important;font-size:13px!important;font-weight:bold!important}'
'.blocklyTreeRow:hover{background:rgba(0,255,102,0.15)!important}'
'.blocklyTreeSelected .blocklyTreeRow{background:#00ff66!important}'
'.blocklyTreeSelected .blocklyTreeLabel{color:#000!important}'
'</style></head><body>'
'<div id="wrap">'
'<canvas id="pCanvas"></canvas>'
'<div id="blocklyDiv"></div>'
'</div>'
)

# â”€â”€ TOOLBOX + SCRIPT OPEN â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
H += BR.TOOLBOX_XML
H += '<script>'
H += (
"var Streamlit={"
"setComponentReady:function(){window.parent.postMessage({isStreamlitMessage:true,type:'streamlit:componentReady',apiVersion:1},'*');},"
"setComponentValue:function(value){window.parent.postMessage({isStreamlitMessage:true,type:'streamlit:setComponentValue',value:value},'*');},"
"setFrameHeight:function(height){window.parent.postMessage({isStreamlitMessage:true,type:'streamlit:setFrameHeight',height:height},'*');}"
"};"
"Streamlit.setComponentReady();Streamlit.setFrameHeight(850);"
)

# â”€â”€ PARTICLES â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
H += (
"var pc=document.getElementById('pCanvas'),px=pc.getContext('2d'),pw,ph,pts=[],mo={x:null,y:null};"
"function rz(){pw=window.innerWidth;ph=window.innerHeight;pc.width=pw;pc.height=ph;}"
"window.addEventListener('resize',rz);rz();"
"window.addEventListener('mousemove',function(e){mo.x=e.clientX;mo.y=e.clientY;});"
"for(var i=0;i<50;i++)pts.push({x:Math.random()*1200,y:Math.random()*700,vx:(Math.random()-.5)*1.5,vy:(Math.random()-.5)*1.5});"
"function ap(){"
"px.clearRect(0,0,pw,ph);"
"pts.forEach(function(p){"
"p.x+=p.vx;p.y+=p.vy;"
"if(p.x<0||p.x>pw)p.vx*=-1;if(p.y<0||p.y>ph)p.vy*=-1;"
"px.beginPath();px.arc(p.x,p.y,1.5,0,Math.PI*2);px.fillStyle='rgba(0,255,102,.7)';px.fill();"
"if(mo.x!=null){var dx=mo.x-p.x,dy=mo.y-p.y,d=Math.sqrt(dx*dx+dy*dy);"
"if(d<160){px.beginPath();px.strokeStyle='rgba(0,255,102,'+(1-d/160)+')';px.lineWidth=1;px.moveTo(p.x,p.y);px.lineTo(mo.x,mo.y);px.stroke();}}"
"pts.forEach(function(q){var dx=p.x-q.x,dy=p.y-q.y,d=Math.sqrt(dx*dx+dy*dy);"
"if(d<100){px.beginPath();px.strokeStyle='rgba(0,255,102,'+(0.15-d/700)+')';px.lineWidth=.5;px.moveTo(p.x,p.y);px.lineTo(q.x,q.y);px.stroke();}});"
"});requestAnimationFrame(ap);}ap();"
)

# â”€â”€ BLOCK DEFINITIONS + GENERATORS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
H += BR.BLOCK_DEFINITIONS_JS
H += (
"if(!Blockly.Python&&typeof pythonGenerator!=='undefined'){Blockly.Python=pythonGenerator;}"
"if(!Blockly.Python){throw new Error('Blockly Python generator failed to load.');}"
)
H += BR.PYTHON_GENERATORS_JS
H += (
"if(Blockly.Python.forBlock){"
"['when_sequence_activated','action_wait_task','custom_input_string',"
"'global_phone_preset','custom_phone_signature','action_dns_resolve',"
"'action_ip_geolocation','action_phone_tracker','action_whois_lookup',"
"'action_robots_sitemap','action_ssl_audit','action_shodan_lookup',"
"'action_http_header_audit','action_service_enum','action_regex_filter',"
"'action_port_scan','action_directory_probe','action_sql_error_detect',"
"'action_xss_reflect_check','action_firewall_detect','action_malware_hash_check']"
".forEach(function(name){if(Blockly.Python[name]){Blockly.Python.forBlock[name]=Blockly.Python[name];}});"
"}"
)

# â”€â”€ BLOCKLY INIT â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
H += (
"window.ws=Blockly.inject('blocklyDiv',{"
"toolbox:document.getElementById('toolbox'),"
"grid:{spacing:40,length:40,colour:'rgba(0,255,102,0.15)',snap:true},"
"move:{scrollbars:true,drag:true,wheel:true},"
"zoom:{controls:true,wheel:true,startScale:1.0,maxScale:3,minScale:0.3,scaleSpeed:1.2},"
"trashcan:true});"
"window.workspace=window.ws;"
"window.ezCompileSequences=function(){"
"var roots=window.ws.getTopBlocks(true).filter(function(b){return b.type==='when_sequence_activated';});"
"if(!roots.length){return Blockly.Python.workspaceToCode(window.ws)||'';}"
"var out=[];"
"roots.forEach(function(b){"
"var code=Blockly.Python.blockToCode(b);"
"if(Array.isArray(code)) code=code[0];"
"if(code) out.push(code);"
"});"
"return out.join('\\n');};"
"window.ezSendState=function(action,extra){"
"extra=extra||{};"
"var code=extra.code!==undefined?extra.code:window.ezCompileSequences();"
"var xml=extra.xml!==undefined?extra.xml:Blockly.Xml.domToText(Blockly.Xml.workspaceToDom(window.ws));"
"Streamlit.setComponentValue({"
"action:action||'sync',code:code,xml:xml,sequenceId:extra.sequenceId||'',aiMsg:extra.aiMsg||'',nonce:String(Date.now())+'-'+Math.random()"
"});"
"};"
"window.ghostCatalog=["
"{name:'Text input',label:'String'},{name:'Number',label:'Number'},{name:'Target string',label:'String'},"
"{name:'Target Domain',label:'String'},{name:'Phone target',label:'String'},{name:'Email target',label:'String'}"
" ];"
)

# â”€â”€ RESTORE XML â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
H += "try{var sx=" + safe_xml + ";if(sx&&sx.trim()!==''){Blockly.Xml.domToWorkspace(Blockly.utils.xml.textToDom(sx),window.ws);}}catch(e){console.error('XML restore:',e);}"

# â”€â”€ TERMINAL HUD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Use single quotes throughout innerHTML so no escaping needed
H += (
"var sv=window.ws.getCanvas();"

"var tfo=document.createElementNS('http://www.w3.org/2000/svg','foreignObject');"
"tfo.setAttribute('x','20');tfo.setAttribute('y','20');"
"tfo.setAttribute('width','400');tfo.setAttribute('height','260');"
"var td=document.createElement('div');td.style.cssText='width:100%;height:100%;';"
"td.innerHTML="
"'<div style=\"width:100%;height:100%;display:flex;flex-direction:column;background:#090d16;border:1px solid #00ff66;border-radius:8px;overflow:hidden;\">'"
"+'<div id=\"th\" style=\"padding:6px 10px;background:#02040a;border-bottom:1px solid #00ff66;font:bold 11px monospace;color:#00ff66;cursor:move;user-select:none;\">&#x1F4BB; TERMINAL</div>'"
"+'<div style=\"flex:1;overflow-y:auto;padding:8px;\"><pre id=\"tlog\" style=\"margin:0;color:#00ff66;font-size:11px;line-height:1.5;white-space:pre-wrap;\"></pre></div>'"
"+'</div>';"
"tfo.appendChild(td);sv.appendChild(tfo);"
"['mousedown','pointerdown','keydown'].forEach(function(ev){td.addEventListener(ev,function(e){e.stopPropagation();});});"
)
H += "document.getElementById('tlog').textContent=" + safe_terminal + ";"
H += "document.getElementById('tlog').parentElement.scrollTop=999999;"

# â”€â”€ AI CHAT HUD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
H += (
"var afo=document.createElementNS('http://www.w3.org/2000/svg','foreignObject');"
"afo.setAttribute('x','440');afo.setAttribute('y','20');"
"afo.setAttribute('width','380');afo.setAttribute('height','500');"
"var ad=document.createElement('div');ad.style.cssText='width:100%;height:100%;';"
"ad.innerHTML="
"'<div style=\"width:100%;height:100%;display:flex;flex-direction:column;background:#090d16;border:1px solid #00ffcc;border-radius:8px;overflow:hidden;\">'"
"+'<div id=\"ah\" style=\"padding:6px 10px;background:#02040a;border-bottom:1px solid #00ffcc;font:bold 11px monospace;color:#00ffcc;cursor:move;user-select:none;\">&#x1F916; AI CO-PILOT</div>'"
"+'<div id=\"achat\" style=\"flex:1;overflow-y:auto;padding:8px;\"></div>'"
"+'<div style=\"padding:6px;background:#02040a;border-top:1px solid #00ffcc;display:flex;gap:5px;\">'"
"+'<input id=\"aiInp\" type=\"text\" placeholder=\"Ask the AI...\" autocomplete=\"off\" style=\"flex:1;background:#05070f;border:1px solid #00ffcc;color:#00ffcc;padding:5px;border-radius:3px;font:11px monospace;\">'"
"+'<button id=\"aiBtn\" style=\"background:#02040a;color:#00ffcc;border:1px solid #00ffcc;padding:4px 10px;cursor:pointer;border-radius:3px;font:bold 11px monospace;\">SEND</button>'"
"+'</div>'"
"+'</div>';"
"afo.appendChild(ad);sv.appendChild(afo);"
"['mousedown','pointerdown','keydown'].forEach(function(ev){ad.addEventListener(ev,function(e){e.stopPropagation();});});"
)

H += (
"var ghostState={block:null,inputIndex:-1,shadow:null,types:[],index:0};"
"function ghostLabelFor(type){"
"if(type==='action_dns_resolve')return 'DNS string';"
"if(type==='action_reverse_dns')return 'Hostname';"
"if(type==='action_hostname_parse')return 'URL or host';"
"if(type==='action_dns_cache_check')return 'Hostname';"
"if(type==='action_ip_geolocation')return 'Hostname';"
"if(type==='action_phone_tracker')return 'Phone number';"
"if(type==='action_email_parse')return 'Email address';"
"if(type==='action_whois_lookup')return 'Domain';"
"if(type==='action_robots_sitemap')return 'URL';"
"if(type==='action_ssl_audit')return 'Hostname';"
"if(type==='action_shodan_lookup')return 'Hostname';"
"if(type==='action_http_header_audit')return 'URL';"
"if(type==='action_service_enum')return 'URL';"
"if(type==='action_regex_filter')return 'Text';"
"if(type==='action_port_scan')return 'Target host';"
"if(type==='action_directory_probe')return 'URL';"
"if(type==='action_sql_error_detect')return 'Target URL';"
"if(type==='action_xss_reflect_check')return 'Target URL';"
"if(type==='action_firewall_detect')return 'Hostname';"
"if(type==='action_malware_hash_check')return 'Hash';"
"if(type==='custom_input_string')return 'String';"
"if(type==='global_phone_preset' || type==='custom_phone_signature')return 'Phone';"
"if(type==='math_number')return 'Number';"
"if(type==='text')return 'Text';"
"return 'Input';}"
"function ghostCandidatesFor(blockType,inputName,checks){"
"var key=String(blockType||'')+'::'+String(inputName||'');"
"if(key==='action_dns_resolve::NAME')return ['custom_input_string'];"
"if(key==='action_reverse_dns::NAME')return ['custom_input_string'];"
"if(key==='action_hostname_parse::NAME')return ['custom_input_string','text'];"
"if(key==='action_dns_cache_check::NAME')return ['custom_input_string'];"
"if(key==='action_ip_geolocation::NAME')return ['custom_input_string'];"
"if(key==='action_phone_tracker::NAME')return ['global_phone_preset','custom_phone_signature'];"
"if(key==='action_email_parse::NAME')return ['custom_input_string','text'];"
"if(key==='action_whois_lookup::NAME')return ['custom_input_string'];"
"if(key==='action_robots_sitemap::NAME')return ['custom_input_string'];"
"if(key==='action_ssl_audit::NAME')return ['custom_input_string'];"
"if(key==='action_shodan_lookup::NAME')return ['custom_input_string'];"
"if(key==='action_http_header_audit::NAME')return ['custom_input_string'];"
"if(key==='action_service_enum::TARGET')return ['custom_input_string'];"
"if(key==='action_regex_filter::NAME')return ['text','custom_input_string'];"
"if(key==='action_port_scan::TARGET')return ['custom_input_string'];"
"if(key==='action_directory_probe::TARGET')return ['custom_input_string'];"
"if(key==='action_sql_error_detect::TARGET')return ['custom_input_string'];"
"if(key==='action_sql_error_detect::PAYLOAD')return ['custom_input_string'];"
"if(key==='action_xss_reflect_check::TARGET')return ['custom_input_string'];"
"if(key==='action_xss_reflect_check::PAYLOAD')return ['custom_input_string'];"
"if(key==='action_firewall_detect::TARGET')return ['custom_input_string'];"
"if(key==='action_malware_hash_check::TARGET')return ['custom_input_string'];"
"return checkToGhostTypes(checks);}"
"function findOpenValueInputBlock(){"
"var blocks=window.ws.getAllBlocks(false);"
"for(var i=0;i<blocks.length;i++){"
"var b=blocks[i];"
"if(!b.inputList)continue;"
"for(var j=0;j<b.inputList.length;j++){"
"var inp=b.inputList[j];"
"if(inp.type===Blockly.INPUT_VALUE&&(!inp.connection||!inp.connection.isConnected())) return {block:b,input:inp,index:j};"
"}}"
"return null;}"
"function checkToGhostTypes(check){"
"var c=Array.isArray(check)?check:(check?[check]:[]);"
"var joined=c.map(function(x){return String(x);}).join(',');"
"if(joined.indexOf('Number')>=0) return ['math_number'];"
"if(joined.indexOf('String')>=0) return ['custom_input_string'];"
"return [];"
"}"
"function ghostBlockDom(type){"
"var xml = Blockly.utils.xml.createElement('xml');"
"var shadow = Blockly.utils.xml.createElement('shadow');"
"shadow.setAttribute('type', type);"
"shadow.setAttribute('id', 'ghost_' + Math.random().toString(36).slice(2));"
"xml.appendChild(shadow);"
"return xml;"
"}"
"function clearGhost(){"
"if(ghostState.shadow){try{ghostState.shadow.dispose(false);}catch(e){} ghostState.shadow=null;}"
"ghostState.block=null;ghostState.inputIndex=-1;ghostState.types=[];ghostState.index=0;"
"}"
"function ensureGhostShadow(){"
"var found=findOpenValueInputBlock();"
"if(!found){if(!ghostState.shadow)return;found={block:ghostState.block?window.ws.getBlockById(ghostState.block):null,input:null,index:ghostState.inputIndex};if(!found.block)return;}"
"var target=found.block;var input=found.input;var inputIndex=found.index;"
"var inputConn=input&&input.connection?input.connection:(target.inputList&&target.inputList[inputIndex]&&target.inputList[inputIndex].connection);"
"if(!inputConn){return;}"
"var checks=(inputConn&&inputConn.check_)||[];"
"var types=ghostCandidatesFor(target.type, input.name, checks);"
"if(!types.length){types=checkToGhostTypes(checks);}"
"if(!types.length){return;}"
"var changed=ghostState.block!==target.id||ghostState.inputIndex!==inputIndex||ghostState.types.join(',')!==types.join(',');"
"ghostState.block=target.id;ghostState.inputIndex=inputIndex;ghostState.types=types;"
"if(changed){ghostState.index=0;}"
"var type=types[ghostState.index % types.length];"
"if(ghostState.shadow&&ghostState.shadow.type===type&&ghostState.shadow.outputConnection&&ghostState.shadow.outputConnection.targetConnection===inputConn){return;}"
"var previous = ghostState.shadow;"
"var created = null;"
"try{created = window.ws.newBlock(type);}catch(e){}"
"if(!created){return;}"
"try{created.setShadow(true);}catch(e){}"
"try{created.initSvg();created.render(false);}catch(e){}"
"try{created.outputConnection.check_ = checks;}catch(e){}"
"try{inputConn.connect(created.outputConnection); ghostState.shadow = created;}catch(e){try{created.dispose(false);}catch(_){} return;}"
"if(previous&&previous!==created){try{previous.dispose(false);}catch(e){}}"
"ghostState.index=(ghostState.index+1)%types.length;"
"if(ghostState.shadow){ghostState.shadow.setMovable(false);}"
"}"
"setTimeout(ensureGhostShadow,300);"
)

# â”€â”€ CHAT RENDER â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
H += "var ch=" + safe_chat + ";"
H += (
"function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\\n/g,'<br>');}"
"function rc(){"
"var c=document.getElementById('achat');c.innerHTML='';"
"ch.forEach(function(m){"
"var d=document.createElement('div');"
"d.style.cssText='margin-bottom:9px;padding:6px 9px;border-radius:4px;font:11px monospace;line-height:1.5;word-break:break-word;';"
"if(m.role==='user'){"
"d.style.background='#02040a';d.style.color='#00ffcc';d.style.borderRight='2px solid #00ffcc';"
"d.innerHTML='<div style=\"font-size:9px;color:#556;margin-bottom:2px;\">YOU:</div>'+esc(m.content);"
"}else{"
"d.style.background='#05070f';d.style.color='#e0e0e0';d.style.borderLeft='2px solid #00ffcc';"
"d.innerHTML='<div style=\"font-size:9px;color:#00ffcc;margin-bottom:2px;\">AI:</div>'+esc(m.content);"
"}"
"c.appendChild(d);});"
"c.scrollTop=c.scrollHeight;}rc();"
)

# â”€â”€ AI SEND â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
H += (
"function send(){"
"var inp=document.getElementById('aiInp');"
"var txt=inp.value.trim();if(!txt)return;"
"inp.value='';inp.disabled=true;document.getElementById('aiBtn').textContent='...';"
"ch.push({role:'user',content:txt});rc();"
"window.ezSendState('ai',{aiMsg:txt});}"
"document.getElementById('aiBtn').addEventListener('click',send);"
"document.getElementById('aiInp').addEventListener('keydown',function(e){if(e.key==='Enter')send();});"
)

# â”€â”€ DRAG â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
H += (
"function mkDrag(id,fo){"
"var dr=false,sx=0,sy=0;"
"document.getElementById(id).addEventListener('mousedown',function(e){"
"dr=true;var sc=window.ws.scale||1;"
"sx=e.clientX/sc-parseFloat(fo.getAttribute('x'));"
"sy=e.clientY/sc-parseFloat(fo.getAttribute('y'));"
"e.stopPropagation();e.preventDefault();});"
"document.addEventListener('mousemove',function(e){"
"if(!dr)return;var sc=window.ws.scale||1;"
"fo.setAttribute('x',e.clientX/sc-sx);fo.setAttribute('y',e.clientY/sc-sy);});"
"document.addEventListener('mouseup',function(){dr=false;});}"
"mkDrag('th',tfo);mkDrag('ah',afo);"
)

# â”€â”€ LIVE COMPILE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
H += (
"var lastCode='';var ct=null;"
"var ghostCt=null;"
"function lc(){"
"var code=window.ezCompileSequences();"
"if(!code||code===lastCode)return;"
"lastCode=code;"
"var xml=Blockly.Xml.domToText(Blockly.Xml.workspaceToDom(window.ws));"
"window.ezSendState('sync',{code:code,xml:xml});}"
"window.ws.addChangeListener(function(e){"
"if([Blockly.Events.BLOCK_CREATE,Blockly.Events.BLOCK_MOVE,"
"Blockly.Events.BLOCK_CHANGE,Blockly.Events.BLOCK_DELETE].indexOf(e.type)>=0){"
"clearTimeout(ct);ct=setTimeout(lc,2000);"
"clearTimeout(ghostCt);ghostCt=setTimeout(ensureGhostShadow,120);}});"
)

# â”€â”€ ACTIVATE (right-click) â€” defined in structure_blocks.js but needs ws alias â”€
# window.workspace = window.ws is already set above so the block's customContextMenu works

H += '</script></body></html>'

component_dir = os.path.join(os.path.dirname(__file__), "assets", "blockly_component")
os.makedirs(component_dir, exist_ok=True)
with open(os.path.join(component_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(H)

blockly_component = components.declare_component("ezhack_blockly", path=component_dir)
component_event = blockly_component(default=None, key="ezhack_blockly")

if isinstance(component_event, dict):
    if component_event.get("code") is not None:
        st.session_state["workspace_code"] = component_event.get("code", "")
    if component_event.get("xml") is not None:
        st.session_state["workspace_xml"] = component_event.get("xml", "")

    nonce = component_event.get("nonce")
    if nonce and nonce != st.session_state.get("last_component_nonce"):
        st.session_state["last_component_nonce"] = nonce
        action = component_event.get("action")
        if action == "run":
            seq_id = component_event.get("sequenceId") or "sequence"
            code = st.session_state["workspace_code"].strip()
            st.session_state["terminal"] += f"\nÃ°Å¸Â¤â€“ Sequence [{seq_id}] activated...\n"
            if code:
                try:
                    exec(code, {"run_scan": BR.run_scan, "time": time})
                    st.session_state["terminal"] += "Ã°Å¸Å¸Â¢ Sequence complete.\n"
                except Exception as e:
                    st.session_state["terminal"] += f"Ã°Å¸â€™Â¥ Error: {e}\n"
            else:
                st.session_state["terminal"] += "Ã¢Å¡Â Ã¯Â¸Â No code found. Connect blocks below a SEQUENCE GENERATOR.\n"
            st.rerun()
        elif action == "ai":
            user_text = component_event.get("aiMsg", "").strip()
            if user_text:
                st.session_state["chat"].append({"role": "user", "content": user_text})
                system_prompt = (
                    "You are an AI assistant inside EZHack, a visual block-coding OSINT tool.\n"
                    f"Workspace code:\n{st.session_state['workspace_code']}\n\n"
                    f"Terminal output:\n{st.session_state['terminal'][-800:]}\n\n"
                    "Be concise and hacker-themed."
                )
                reply = ai_reply([{"role": "system", "content": system_prompt}] + st.session_state["chat"])
                st.session_state["chat"].append({"role": "assistant", "content": reply})
                st.rerun()

# â”€â”€ 6. Live code display â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.markdown('<div class="live-code-box">', unsafe_allow_html=True)
st.subheader("ðŸ“ Live Compiled Automation Script")
st.code(st.session_state["workspace_code"] or "# No blocks connected yet.", language="python")
st.markdown('</div>', unsafe_allow_html=True)