import os
import socket
import json
import urllib.request
import urllib.parse
import random
import re
import streamlit as st
import streamlit.components.v1 as components

# Import python-dotenv to read .env file safely
from dotenv import load_dotenv
load_dotenv()

# Import Groq SDK
from groq import Groq

# Import Google's phonenumbers library components
import phonenumbers
from phonenumbers import carrier, geocoder, timezone

# Initialize Groq Client if API key is present
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ai_client = None
if GROQ_API_KEY:
    ai_client = Groq(api_key=GROQ_API_KEY)

# Priority ordered list of your models for rate-limit and token failover rotation
AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b"
]

# ==========================================
# 1. CORE UTILITY FUNCTIONS (PASSIVE OSINT SUITE)
# ==========================================

def perform_dns_lookup(target: str) -> str:
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    clean_host = clean_host.replace("https://", "").replace("http://", "").split("/")[0]
    if not clean_host:
        return "❌ ERROR: Target missing!"
    
    if clean_host.startswith("+") or (clean_host.isdigit() and len(clean_host) > 6):
        return perform_phone_tracking(clean_host)
        
    try:
        ip_addr = socket.gethostbyname(clean_host)
        return f"🌐 [DNS REPORT]\n🔹 Target Host: {clean_host}\n📍 Resolved Target IPv4: {ip_addr}\n💡 Extraction Successful."
    except Exception as err:
        return f"❌ DNS Resolve Failed for '{clean_host}': {str(err)}"

def perform_phone_tracking(phone_input: str) -> str:
    clean_num = str(phone_input).strip().replace(" ", "")
    if not clean_num.startswith("+"):
        clean_num = "+" + clean_num
        
    try:
        parsed_num = phonenumbers.parse(clean_num, None)
        if not phonenumbers.is_valid_number(parsed_num):
            return f"❌ Target validation check failed: '{clean_num}' is not a valid global structure."
            
        region = geocoder.description_for_number(parsed_num, "en")
        operator = carrier.name_for_number(parsed_num, "en")
        zones = timezone.time_zones_for_number(parsed_num)
        
        return (
            f"📱 [TELECOM OSINT REPORT]\n"
            f"🔹 Normalized E.164 Identity: {clean_num}\n"
            f"🔹 Geo-Location Cluster: {region if region else 'Unknown/Global Routing'}\n"
            f"🔹 Carrier/Network Provider: {operator if operator else 'Virtual / MVNO / Unlisted'}\n"
            f"🔹 Assigned Timezones: {', '.join(zones)}\n"
            f"💡 Passive SigInt trace finished."
        )
    except Exception as err:
        return f"❌ Telecom tracking subsystem failure: {str(err)}"

def perform_ip_tracking(ip_input: str) -> str:
    clean_ip = str(ip_input).strip().replace(" ", "")
    if not clean_ip:
        return "❌ ERROR: Missing target IPv4 footprint."
        
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", clean_ip):
        return perform_dns_lookup(clean_ip)
        
    try:
        url = f"http://ip-api.com/json/{clean_ip}?fields=status,message,country,regionName,city,zip,lat,lon,isp,org,as,query"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            
        if data.get("status") == "fail":
            return f"❌ Geo-IP Routing Matrix Error: {data.get('message', 'Unknown failure')}"
            
        return (
            f"🎯 [GEO-IP RECON MATRIX REPORT]\n"
            f"🔹 Footprint Address: {data.get('query')}\n"
            f"🔹 Country Backbone: {data.get('country')} ({data.get('zip', 'N/A')})\n"
            f"🔹 Coordinate Cluster: LAT {data.get('lat')} / LON {data.get('lon')}\n"
            f"🔹 ISP Node: {data.get('isp')}\n"
            f"🔹 AS Routing Registry: {data.get('as')}\n"
            f"💡 Physical infrastructure trace completed."
        )
    except Exception as err:
        return f"❌ Network Geo-Registry timeout or error: {str(err)}"

def generate_random_osint_data(data_type: str) -> str:
    if data_type == "IP":
        ip = f"{random.randint(1,254)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
        return f"🎲 Simulated Target IPv4 Node Generated: {ip}"
    elif data_type == "Phone":
        cc = random.choice(["1", "44", "62", "81", "33", "49"])
        body = "".join(str(random.randint(0,9)) for _ in range(9))
        return f"🎲 Simulated Target Telecom Target Generated: +{cc}{body}"
    return "❌ Unsupported generation profile."

def execute_crypto_hashing(text_input: str, algo: str) -> str:
    import hashlib
    b_data = str(text_input).encode('utf-8')
    if algo == "MD5":
        return f"🔑 MD5 Hash Result: {hashlib.md5(b_data).hexdigest()}"
    elif algo == "SHA-1":
        return f"🔑 SHA-1 Hash Result: {hashlib.sha1(b_data).hexdigest()}"
    elif algo == "SHA-256":
        return f"🔑 SHA-256 Hash Result: {hashlib.sha256(b_data).hexdigest()}"
    return "❌ Unsupported algorithm block specified."

def execute_base64_transform(text_input: str, mode: str) -> str:
    import base64
    try:
        if mode == "Encode":
            res = base64.b64encode(str(text_input).encode('utf-8')).decode('utf-8')
            return f"🔒 Base64 Cipher Output: {res}"
        else:
            res = base64.b64decode(str(text_input).encode('utf-8')).decode('utf-8')
            return f"🔓 Base64 Plaintext Recovery: {res}"
    except Exception as err:
        return f"❌ Data processing codec failure: {str(err)}"

# ==========================================
# 2. RUNTIME SYSTEM STATE LOGS
# ==========================================
if "synced_workspace_code" not in st.session_state:
    st.session_state["synced_workspace_code"] = "# No compiled code blocks found in current frame workspace context."

if "terminal_history_output" not in st.session_state:
    st.session_state["terminal_history_output"] = "📟 EZHack Shell v2.1.0 Initialized... Ready for user operational context.\n"

if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = [
        {"role": "assistant", "content": "Greetings Operator. Autonomous AI Copilot module is attached to current tool environment. How can I assist with your pentesting operations?"}
    ]

# ==========================================
# 3. INITIAL STREAMLIT PAGE LAYOUT
# ==========================================
st.set_page_config(page_title="EZHack Dashboard", layout="wide")
st.title("💻 EZHack Pentesting Multi-Tool Dashboard")
st.caption("Integrated OSINT Framework, Network Utilities, & Autonomous AI Copilot")

# Build Navigation tabs
tab1, tab2, tab3 = st.tabs(["Tab 1: Visual Workspace 🧩", "Tab 2: Utilities & OSINT 🔍", "Tab 3: AI Copilot 🤖"])

# Handle actions sent from the internal custom iframe canvas workspace back to Streamlit URL query string parameters
query_params = st.query_params
if "action" in query_params:
    act = query_params["action"]
    tgt = query_params.get("target", "")
    param = query_params.get("param", "")
    
    log_entry = ""
    if act == "dns":
        log_entry = perform_dns_lookup(tgt)
    elif act == "ip_track":
        log_entry = perform_ip_tracking(tgt)
    elif act == "phone_track":
        log_entry = perform_phone_tracking(tgt)
    elif act == "gen_ip":
        log_entry = generate_random_osint_data("IP")
    elif act == "gen_phone":
        log_entry = generate_random_osint_data("Phone")
    elif act == "hash":
        log_entry = execute_crypto_hashing(tgt, param)
    elif act == "b64":
        log_entry = execute_base64_transform(tgt, param)
        
    if log_entry:
        st.session_state["terminal_history_output"] += f"\n> Executing block event: {act.upper()}\n{log_entry}\n"
        
    if "code" in query_params:
        st.session_state["synced_workspace_code"] = urllib.parse.unquote(query_params["code"])
        
    # Clear query parameters and refresh application frame layout context
    st.query_params.clear()
    st.rerun()

# ------------------------------------------
# TAB 1: VISUAL NODE WORKSPACE
# ------------------------------------------
with tab1:
    st.subheader("🧩 Node Logic Workspace Constructor")
    st.write("Drag, link, and wire up execution logic arrays. Build custom automated intelligence routines.")
    
    # Large custom HTML canvas logic board environment injection
    workspace_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: 'Courier New', monospace; background: #0d1117; color: #58a6ff; margin:0; padding:10px; user-select: none; overflow: hidden; }
            #canvas-container { position: relative; width: 100%; height: 440px; background: #161b22; border: 2px dashed #30363d; border-radius: 8px; }
            canvas { display: block; }
            .sidebar-blocks { display: flex; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; background: #21262d; padding: 8px; border-radius: 6px; }
            .block-btn { background: #238636; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size:12px; }
            .block-btn:hover { background: #2ea043; }
            .danger-btn { background: #da3637; } .danger-btn:hover { background: #f85149; }
            #target-input-box { background: #0d1117; border: 1px solid #30363d; color: #58a6ff; padding: 6px; border-radius: 4px; width: 220px; font-family: inherit; }
            .controls-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
            select { background: #0d1117; border: 1px solid #30363d; color: #58a6ff; padding: 5px; border-radius:4px; font-family: inherit; }
        </style>
    </head>
    <body>

        <div class="controls-row">
            <label for="target-input-box">🎯 Core Execution Target Matrix: </label>
            <input type="text" id="target-input-box" value="google.com" placeholder="IP, Domain, Phone, or Text string...">
            
            <label style="margin-left:15px;">⚙️ Hash Configuration: </label>
            <select id="algo-param">
                <option value="SHA-256">SHA-256</option>
                <option value="MD5">MD5</option>
                <option value="SHA-1">SHA-1</option>
            </select>

            <label style="margin-left:15px;">⚙️ Base64 Mode: </label>
            <select id="b64-param">
                <option value="Encode">B64 Encode</option>
                <option value="Decode">B64 Decode</option>
            </select>
        </div>

        <div class="sidebar-blocks">
            <button class="block-btn" onclick="addNode('DNS Lookup', '#1f6feb', 'dns')">🌐 DNS Lookup</button>
            <button class="block-btn" onclick="addNode('Geo-IP Tracker', '#8957e5', 'ip_track')">🎯 Geo-IP Trace</button>
            <button class="block-btn" onclick="addNode('Telecom SigInt', '#da5b0b', 'phone_track')">📱 Phone Tracker</button>
            <button class="block-btn" onclick="addNode('Gen Random IP', '#0e4429', 'gen_ip')">🎲 Gen IP</button>
            <button class="block-btn" onclick="addNode('Gen Phone Target', '#0e4429', 'gen_phone')">🎲 Gen Phone</button>
            <button class="block-btn" onclick="addNode('Crypto Hashing', '#6e7681', 'hash')">🔑 Hash String</button>
            <button class="block-btn" onclick="addNode('Base64 Codec', '#6e7681', 'b64')">🔒 Base64 Transform</button>
            <button class="block-btn danger-btn" onclick="clearWorkspace()">🧹 Clear Board</button>
        </div>

        <div id="canvas-container">
            <canvas id="blockCanvas" width="900" height="440"></canvas>
        </div>

        <script>
            const canvas = document.getElementById('blockCanvas');
            const ctx = canvas.getContext('2d');
            let nodes = [];
            let draggingNode = null;
            let offsetX = 0;
            let offsetY = 0;

            function resizeCanvas() {
                canvas.width = canvas.parentElement.clientWidth;
                draw();
            }
            window.addEventListener('resize', resizeCanvas);

            function addNode(name, color, type) {
                nodes.push({
                    id: Date.now() + Math.random(),
                    x: 50 + (nodes.length * 25) % 300,
                    y: 80 + (nodes.length * 30) % 200,
                    w: 210,
                    h: 55,
                    name: name,
                    color: color,
                    type: type
                });
                syncCodeRepresentation();
                draw();
            }

            function clearWorkspace() {
                nodes = [];
                syncCodeRepresentation();
                draw();
            }

            function syncCodeRepresentation() {
                let codeStr = "import os\\nimport ezhack_core\\n\\n# Compiled Execution Pipeline State Array:\\n";
                if(nodes.length === 0) {
                    codeStr += "# Workspace structure evaluates to empty state.";
                }
                nodes.forEach((n, idx) => {
                    codeStr += `step_${idx + 1} = ezhack_core.trigger_node(action="${n.type}")\\n`;
                });
                
                // We use a clean execution layer pipeline fallback injection
                const encodedCode = encodeURIComponent(codeStr);
            }

            function triggerNodeExecution(node) {
                const targetVal = document.getElementById('target-input-box').value;
                const algoVal = document.getElementById('algo-param').value;
                const b64Val = document.getElementById('b64-param').value;
                
                let paramValue = "";
                if(node.type === 'hash') paramValue = algoVal;
                if(node.type === 'b64') paramValue = b64Val;

                let codeStr = "import os\\nimport ezhack_core\\n\\n";
                nodes.forEach((n, idx) => {
                    codeStr += `step_${idx + 1} = ezhack_core.trigger_node(action="${n.type}")\\n`;
                });

                // Blast parameters up to parent layout stream context frames
                const url = `?action=${node.type}&target=${encodeURIComponent(targetVal)}&param=${encodeURIComponent(paramValue)}&code=${encodeURIComponent(codeStr)}`;
                window.parent.location.href = url;
            }

            function draw() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // Grid background drawing sequence
                ctx.strokeStyle = '#21262d';
                ctx.lineWidth = 1;
                for(let x = 0; x < canvas.width; x += 30) {
                    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
                }
                for(let y = 0; y < canvas.height; y += 30) {
                    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
                }

                // Link path tracing logic pipeline connection rendering
                if(nodes.length > 1) {
                    ctx.strokeStyle = '#58a6ff';
                    ctx.lineWidth = 3;
                    ctx.setLineDash([4, 4]);
                    for(let i = 0; i < nodes.length - 1; i++) {
                        ctx.beginPath();
                        ctx.moveTo(nodes[i].x + nodes[i].w / 2, nodes[i].y + nodes[i].h);
                        ctx.lineTo(nodes[i+1].x + nodes[i+1].w / 2, nodes[i+1].y);
                        ctx.stroke();
                    }
                    ctx.setLineDash([]);
                }

                // Draw standard active component block containers
                nodes.forEach(n => {
                    ctx.fillStyle = '#161b22';
                    ctx.strokeStyle = n.color;
                    ctx.lineWidth = 2;
                    ctx.beginPath();
                    ctx.roundRect(n.x, n.y, n.w, n.h, 6);
                    ctx.fill();
                    ctx.stroke();

                    // Font rendering elements specifications
                    ctx.fillStyle = '#c9d1d9';
                    ctx.font = 'bold 12px "Courier New", monospace';
                    ctx.fillText(n.name, n.x + 12, n.y + 24);

                    // Render node internal functional button components
                    ctx.fillStyle = n.color;
                    ctx.beginPath();
                    ctx.roundRect(n.x + n.w - 85, n.y + 32, 75, 16, 3);
                    ctx.fill();

                    ctx.fillStyle = '#ffffff';
                    ctx.font = '9px "Courier New", monospace';
                    ctx.fillText("⚡ RUN NODE", n.x + n.w - 80, n.y + 43);
                });
            }

            canvas.addEventListener('mousedown', e => {
                const rect = canvas.getBoundingClientRect();
                const mouseX = e.clientX - rect.left;
                const mouseY = e.clientY - rect.top;

                for (let i = nodes.length - 1; i >= 0; i--) {
                    let n = nodes[i];
                    
                    // Click validation check target context boundary boxes for active execute buttons
                    if (mouseX >= n.x + n.w - 85 && mouseX <= n.x + n.w - 10 &&
                        mouseY >= n.y + 32 && mouseY <= n.y + 48) {
                        triggerNodeExecution(n);
                        return;
                    }
                    
                    // Boundary frame tracking validation for standard card drags
                    if (mouseX >= n.x && mouseX <= n.x + n.w &&
                        mouseY >= n.y && mouseY <= n.y + n.h) {
                        draggingNode = n;
                        offsetX = mouseX - n.x;
                        offsetY = mouseY - n.y;
                        
                        // Shift matching identity layer straight back out to high execution priority arrays
                        nodes.splice(i, 1);
                        nodes.push(draggingNode);
                        break;
                    }
                }
            });

            canvas.addEventListener('mousemove', e => {
                if (!draggingNode) return;
                const rect = canvas.getBoundingClientRect();
                draggingNode.x = e.clientX - rect.left - offsetX;
                draggingNode.y = e.clientY - rect.top - offsetY;
                draw();
            });

            canvas.addEventListener('mouseup', () => {
                if(draggingNode) syncCodeRepresentation();
                draggingNode = null;
            });

            // Delay initialization briefly to allow parent browser frames layout settling cycles
            setTimeout(resizeCanvas, 100);
        </script>
    </body>
    </html>
    """
    components.html(workspace_html, height=530, scrolling=False)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📟 Live Output Terminal Engine Log")
        st.code(st.session_state["terminal_history_output"], language="bash")
    with col2:
        st.subheader("📜 Auto-Compiled Python Automation Workspace Code")
        st.code(st.session_state["synced_workspace_code"], language="python")

# ------------------------------------------
# TAB 2: UTILITIES & OSINT
# ------------------------------------------
with tab2:
    st.subheader("🔍 Passive Reconnaissance & Crypto Utilities Module")
    st.write("Direct interface panels bypassing the drag-and-drop workspace framework.")
    
    util_mode = st.selectbox("Select Utility Module to Activate:", [
        "DNS Information Extractor", 
        "Network Geo-IP Tracker", 
        "Telecom Metadata Tracer",
        "Cryptographic Hashing Engine",
        "Base64 Transcoder Platform"
    ])
    
    st.markdown("---")
    
    if util_mode == "DNS Information Extractor":
        tgt_domain = st.text_input("Enter Target Host Domain Name:", "example.com")
        if st.button("Launch DNS Fingerprinting Event"):
            res = perform_dns_lookup(tgt_domain)
            st.info(res)
            
    elif util_mode == "Network Geo-IP Tracker":
        tgt_ip = st.text_input("Enter Target IPv4 Endpoint Footprint:", "8.8.8.8")
        if st.button("Query Physical Grid Geo-Location"):
            res = perform_ip_tracking(tgt_ip)
            st.info(res)
            
    elif util_mode == "Telecom Metadata Tracer":
        tgt_phone = st.text_input("Enter Telecom Number Identity (Include international country prefix code):", "+14155552671")
        if st.button("Extract Operator Carrier Signatures"):
            res = perform_phone_tracking(tgt_phone)
            st.info(res)

    elif util_mode == "Cryptographic Hashing Engine":
        hash_str = st.text_area("Enter Raw Data Input String:", "EZHack Workspace Payload Data")
        algo_choice = st.radio("Select Targeting Hash Profile:", ["SHA-256", "MD5", "SHA-1"])
        if st.button("Compute Cryptographic Hash Output"):
            res = execute_crypto_hashing(hash_str, algo_choice)
            st.success(res)

    elif util_mode == "Base64 Transcoder Platform":
        codec_str = st.text_area("Target Plaintext / Cipher Input Data:", "EZHack Data Block Context")
        codec_mode = st.radio("Operation Execution Target Model:", ["Encode", "Decode"])
        if st.button("Process Codec Transform Event"):
            res = execute_base64_transform(codec_str, codec_mode)
            st.success(res)

# ------------------------------------------
# TAB 3: AI COPILOT (WITH AUTOMATED MODEL FALLOVER ROTATION)
# ------------------------------------------
with tab3:
    st.subheader("🤖 Autonomous Tactical Pentesting AI Copilot")
    st.write("Context-aware system hooked into your active layout modules and background workspace compilers.")
    
    if not GROQ_API_KEY:
        st.error("⚠️ AI Subsystems offline: Target Groq Connection Key was not discovered inside active secrets arrays.")
        st.info("To unblock this interface window, append `GROQ_API_KEY` directly inside your environment variables or Streamlit Deployment Cloud Secrets Dashboard.")
    else:
        # Display chat history entries step-by-step
        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        # Handle new user text input sequences
        if user_query := st.chat_input("Input target query instructions for Copilot engine..."):
            with st.chat_message("user"):
                st.markdown(user_query)
            st.session_state["chat_messages"].append({"role": "user", "content": user_query})
            
            # Formulate structured background application status arrays to supply contextual background orientation
            system_context = f"""
            You are the integrated AI Copilot module inside EZHack, an all-in-one advanced utility console built on a visual block-coding platform.
            The user is building security and OSINT tools by dragging logic blocks.
            
            Current compiled workspace Python code:
            {st.session_state.get("synced_workspace_code", "")}
            
            Current output console logs:
            {st.session_state.get("terminal_history_output", "")}
            
            Analyze the user's workspace, explain what their blocks are doing, and answer their prompt. Keep it hacker-themed, concise, and educational. Do not generate destructive payloads.
            """
            
            # Pack standard chronological frame list formatting arrays
            api_messages = [{"role": "system", "content": system_context}] + st.session_state["chat_messages"]
            
            response_text = None
            
            # Loop sequentially through the specified priority model tier pool if rate boundaries or API failures occur
            for model_name in AVAILABLE_MODELS:
                try:
                    with st.spinner(f"🤖 Consulting model tier node: {model_name}..."):
                        response = ai_client.chat.completions.create(
                            model=model_name,
                            messages=api_messages,
                        )
                    response_text = response.choices[0].message.content
                    st.toast(f"✅ Successfully established pipeline with {model_name}")
                    break  # Found a responsive endpoint; break out of the fallback loop safely
                    
                except Exception as api_err:
                    # Capture rate limits, depleted token balances, or connection blocks and transition to the next model node
                    st.warning(f"⚠️ Model node {model_name} unavailable or rate-limited. Shifting down the routing matrix...")
                    continue
            
            # Display response output if any model in the list was successfully queried
            if response_text:
                with st.chat_message("assistant"):
                    st.markdown(response_text)
                st.session_state["chat_messages"].append({"role": "assistant", "content": response_text})
                st.rerun()
            else:
                st.error("🚨 Critical Error: All specified model routing configurations are exhausted or non-responsive.")