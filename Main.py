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
# Load HTML template from file — keeps JS completely separate from Python,
# no f-string or escaping issues possible.
import os as _os
_template_path = _os.path.join(_os.path.dirname(__file__), "assets", "workspace.html")
with open(_template_path, "r", encoding="utf-8") as _f:
    _html_template = _f.read()

blockly_html_payload = (
    _html_template
    .replace("%%TOOLBOX_XML%%",          blocks_registry.TOOLBOX_XML)
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