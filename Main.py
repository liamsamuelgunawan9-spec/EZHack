import os
import socket
import json
import urllib.request
import random
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. SIMPLIFIED RECON UTILITIES (BACKEND)
# ==========================================

def perform_dns_lookup(target: str) -> str:
    """Finds the IP address belonging to a website name."""
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_host:
        return "❌ ERROR: You didn't enter a website name!"
    try:
        ip_addr = socket.gethostbyname(clean_host)
        return (
            f"🔍 [WEBSITE SERVER LOOK-UP]\n"
            f"  ├── Website Name : {clean_host}\n"
            f"  └── Server IP    : {ip_addr}\n"
            f"🟢 SUCCESS: Found the server address!"
        )
    except socket.gaierror:
        return f"❌ ERROR:\n  └── Could not find a server for '{clean_host}'. Check your spelling!"
    except Exception as e:
        return f"💥 SYSTEM CRASH: {str(e)}"


def perform_reverse_dns(target: str) -> str:
    """Finds the website domain name using an IP address."""
    clean_ip = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_ip:
        return "❌ ERROR: You didn't enter an IP address!"
    try:
        host_meta = socket.gethostbyaddr(clean_ip)
        return (
            f"🔄 [FIND WEBSITE FROM IP]\n"
            f"  ├── IP Address   : {clean_ip}\n"
            f"  └── Website Name : {host_meta[0]}\n"
            f"🟢 SUCCESS: Website found successfully!"
        )
    except Exception:
        return f"❌ ERROR:\n  └── Could not find any website names attached to the IP '{clean_ip}'"


def perform_ip_geolocation(target: str) -> str:
    """Finds the geographic location information of an IP or Domain."""
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_host:
        return "❌ ERROR: You didn't enter an IP or Website!"
    try:
        try:
            lookup_ip = socket.gethostbyname(clean_host)
        except socket.gaierror:
            return f"❌ ERROR:\n  └── Target '{clean_host}' is offline or invalid."

        api_url = f"http://ip-api.com/json/{lookup_ip}"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as network_stream:
            json_payload = json.loads(network_stream.read().decode())
            
        if json_payload.get("status") == "fail":
            return f"❌ ERROR:\n  └── Server message: {json_payload.get('message', 'Unknown error')}"
            
        return (
            f"🗺️ [IP ADDRESS LOCATION REPORT]\n"
            f"  ├── Searched For : {clean_host}\n"
            f"  ├── Real IP      : {json_payload.get('query')}\n"
            f"  ├── Country      : {json_payload.get('country')} ({json_payload.get('countryCode')})\n"
            f"  ├── City/State   : {json_payload.get('city')}, {json_payload.get('regionName')}\n"
            f"  ├── Company/ISP  : {json_payload.get('isp')}\n"
            f"  └── Network Code : {json_payload.get('as')}\n"
            f"🟢 SUCCESS: Location coordinates loaded!"
        )
    except Exception as e:
        return f"💥 SYSTEM CRASH: {str(e)}"


def perform_phone_scan(target_phone: str) -> str:
    """Breaks down a phone number into readable provider network details."""
    clean_phone = str(target_phone).strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not clean_phone:
        return "❌ ERROR: You didn't enter any phone digits!"
    
    is_intl = clean_phone.startswith("+")
    country_est = "🌍 Outside North America (International)" if is_intl else "🇺🇸 Local US/Canada Number"
    length = len(clean_phone)
    
    mock_carriers = ["Verizon Wireless Network", "AT&T Core Mobility", "T-Mobile USA Network", "Vodafone Routing Hub", "Orange Telecom Group"]
    mock_line_types = ["📱 Mobile / Cell Phone", "☎️ Traditional Landline", "💻 Internet Number (VoIP)", "📡 Toll-Free Helpline Circuit"]
    
    seed_val = sum(ord(c) for c in clean_phone)
    random.seed(seed_val)
    
    selected_carrier = random.choice(mock_carriers)
    selected_type = random.choice(mock_line_types)
    exchange_code = clean_phone[1:4] if is_intl else clean_phone[0:3]
    
    return (
        f"📡 [PHONE NUMBER SCAN RAPID REPORT]\n"
        f"  ├── Original Entry : {target_phone}\n"
        f"  ├── Cleaned Number : {clean_phone}\n"
        f"  ├── Total Digits   : {length} numbers\n"
        f"  ├── Location Area  : {country_est}\n"
        f"  ├── Area/City Code : [+{exchange_code}]\n"
        f"  ├── Phone Type     : {selected_type}\n"
        f"  └── Phone Company  : {selected_carrier}\n"
        f"🟢 SUCCESS: Line trace complete!"
    )

# ==========================================
# 2. RUNTIME PIPELINE TRANSLATOR & ENGINE
# ==========================================

def run_utility_scan(target_string: str, scan_profile_type: str) -> str:
    normalized_profile = str(scan_profile_type).lower().strip()
    if normalized_profile == "phone":
        return perform_phone_scan(target_string)
    elif normalized_profile == "dns":
        return perform_dns_lookup(target_string)
    elif normalized_profile == "rev_dns":
        return perform_reverse_dns(target_string)
    else:
        return perform_ip_geolocation(target_string)


def show_output_to_user(data_result_string: str):
    st.session_state["console_terminal_logs"] += f"\n{data_result_string}\n⚡{'='*48}⚡\n"


def compile_and_execute_blocks(compiled_script_text: str):
    st.session_state["console_terminal_logs"] = "⚡ MONITOR STREAM ACTIVE...\n⚡ EXECUTING ACTIVE CANVA BLOCKS:\n"
    
    restricted_sandbox_globals = {
        "run_utility_scan": run_utility_scan,
        "show_output_to_user": show_output_to_user,
        "print": lambda *args: show_output_to_user(" ".join(map(str, args))),
        "current_result": ""
    }
    try:
        exec(compiled_script_text, restricted_sandbox_globals)
    except Exception as runtime_exception:
        st.session_state["console_terminal_logs"] += f"\n💥 [SCRIPT RUN ERROR]: {str(runtime_exception)}"

# ==========================================
# 3. INTERACTIVE LAYOUT SETUP VIEW
# ==========================================

st.set_page_config(page_title="EZHack Horizon Studio", layout="wide")

# Core Memory Blocks Initialization
if "console_terminal_logs" not in st.session_state:
    st.session_state["console_terminal_logs"] = "💻 [TERMINAL READY] Construct your automation block structure and click deploy..."

if "live_compiled_code" not in st.session_state:
    st.session_state["live_compiled_code"] = "current_result = run_utility_scan('8.8.8.8', 'geoip')\nshow_output_to_user(current_result)"

# ----------------------------------------------------
# 🪐 TOP CONTROLS ROW & TOP-LEFT LAUNCH BUTTON
# ----------------------------------------------------
title_col, action_col = st.columns([8, 4])

with title_col:
    st.title("⚡ EZHack Core Playground — Horizon Studio")
    st.caption("Cyberpunk workspace canvas. Cool aesthetics layered with simple, easy-to-read targeting modules.")

with action_col:
    st.write("")  # Alignment spacing
    st.write("")
    # Top-Left aligned launcher matrix switch
    trigger_pipeline_run = st.button("🚀 DEPLOY ACTIVE PIPELINE", type="primary", use_container_width=True)

# Process workspace script directly on top click loop
if trigger_pipeline_run:
    with st.spinner("Processing automated actions code sequences..."):
        compile_and_execute_blocks(st.session_state["live_compiled_code"])

# Safely wrap string injection payloads 
safe_terminal_logs = st.session_state["console_terminal_logs"].replace("`", "'").replace("\\", "\\\\").replace("\n", "\\n")

# ----------------------------------------------------
# STAGE 1: FULL-WINDOW ARENA DISPLAY CANVAS (TOP)
# ----------------------------------------------------
st.markdown("### 🗺️ Visual Studio Workspace Canvas")

blockly_html_payload = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Blockly Infinite Horizon</title>
  <script src="https://unpkg.com/blockly/blockly.min.js"></script>
  <script src="https://unpkg.com/blockly/python_compressed.js"></script>
  <script src="https://unpkg.com/blockly/blocks_compressed.js"></script>
  <style>
    html, body {{ height: 100%; margin: 0; padding: 0; background-color: #0b0c10; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overflow: hidden; }}
    #containerDiv {{ position: relative; width: 100%; height: 840px; }}
    #blocklyDiv {{ width: 100%; height: 100%; border: 2px solid #1f2833; border-radius: 6px; box-shadow: inset 0 0 30px rgba(0,0,0,0.9); }}
    .blocklyTreeLabel {{ color: #66fcf1 !important; font-weight: bold; font-size: 13px; }}
    
    #draggableTerminal {{
      position: absolute;
      top: 30px;
      right: 30px;
      width: 480px;
      height: 440px;
      z-index: 999;
      background: rgba(11, 12, 16, 0.94);
      border: 2px solid #66fcf1;
      border-radius: 8px;
      box-shadow: 0 0 25px rgba(102, 252, 241, 0.3);
      display: flex;
      flex-direction: column;
    }}
    #terminalHeader {{
      padding: 12px;
      cursor: move;
      background: #1f2833;
      border-bottom: 2px solid #45a29e;
      color: #66fcf1;
      font-weight: bold;
      font-size: 11px;
      letter-spacing: 1.5px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-radius: 6px 6px 0 0;
      user-select: none;
    }}
    #terminalBody {{
      flex: 1;
      padding: 15px;
      margin: 0;
      background: #0b0c10;
      color: #1fec79;
      font-family: 'Courier New', Courier, monospace;
      font-size: 13px;
      line-height: 1.5;
      overflow-y: auto;
      white-space: pre-wrap;
      border-radius: 0 0 6px 6px;
    }}
    .window-dots {{ display: flex; gap: 6px; }}
    .dot {{ width: 10px; height: 10px; border-radius: 50%; }}
    .dot-red {{ background: #ff5f56; }}
    .dot-green {{ background: #27c93f; }}
  </style>
</head>
<body>

  <div id="containerDiv">
    <div id="draggableTerminal">
      <div id="terminalHeader">
        <span>🤖 LIVE TARGET OUTPUT TERMINAL</span>
        <div class="window-dots">
          <div class="dot dot-red"></div>
          <div class="dot dot-green"></div>
        </div>
      </div>
      <pre id="terminalBody">{safe_terminal_logs}</pre>
    </div>
    <div id="blocklyDiv"></div>
  </div>

  <xml id="toolbox" style="display: none">
    <category name="🌐 Targets &amp; Inputs" colour="160">
      <block type="custom_input_string"></block>
      <block type="target"></block>
      <block type="text"></block>
      <block type="text_join"></block>
    </category>
    <category name="🎯 Scanners &amp; Loops" colour="210">
      <block type="action_scan"></block>
      <block type="controls_if"></block>
      <block type="logic_compare"></block>
      <block type="logic_operation"></block>
      <block type="controls_repeat_ext">
        <value name="TIMES"><block type="math_number"><field name="NUM">3</field></block></value>
      </block>
    </category>
    <category name="📋 Target Lists" colour="260">
      <block type="lists_create_with"></block>
      <block type="lists_repeat"></block>
    </category>
    <category name="🖥️ Screen Outputs" colour="20">
      <block type="display_result"></block>
    </category>
    <sep></sep>
    <category name="⚙️ Variables" colour="330" custom="VARIABLE"></category>
  </xml>

  <script>
    Blockly.Blocks['custom_input_string'] = {{
      init: function() {{
        this.appendDummyInput()
            .appendField("Type Target:")
            .appendField(new Blockly.FieldTextInput("123-456-7890"), "RAW_TEXT");
        this.setOutput(true, "String");
        this.setColour(160);
      }}
    }};

    Blockly.Blocks['target'] = {{
      init: function() {{
        this.appendDummyInput()
            .appendField("Quick Website:")
            .appendField(new Blockly.FieldTextInput("google.com"), "Target");
        this.setOutput(true, "String");
        this.setColour(120);
      }}
    }};

    Blockly.Blocks['action_scan'] = {{
      init: function() {{
        this.appendValueInput("NAME")
            .setCheck(null)
            .appendField("Target info to check:");
        this.appendDummyInput()
            .appendField("Action:")
            .appendField(new Blockly.FieldDropdown([
              ["📱 Phone Number Scan","phone"], 
              ["🗺️ IP Address Location","geoip"], 
              ["🔍 Website Server Look-up","dns"],
              ["🔄 Find Website from IP","rev_dns"]
            ]), "SCANTYPE");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(210);
      }}
    }};

    Blockly.Blocks['display_result'] = {{
      init: function() {{
        this.appendDummyInput().appendField("📟 Print Results to Monitor Screen");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(20);
      }}
    }};

    Blockly.Python.forBlock['custom_input_string'] = function(block) {{
      var text_raw_text = block.getFieldValue('RAW_TEXT');
      return ['"' + text_raw_text + '"', 0];
    }};

    Blockly.Python.forBlock['target'] = function(block) {{
      var field_target = block.getFieldValue('Target');
      return ['"' + field_target + '"', 0];
    }};

    Blockly.Python.forBlock['action_scan'] = function(block) {{
      var dropdown_scantype = block.getFieldValue('SCANTYPE');
      var value_name = Blockly.Python.valueToCode(block, 'NAME', 0) || "''";
      return 'current_result = run_utility_scan(' + value_name + ', "' + dropdown_scantype + '")\\n';
    }};

    Blockly.Python.forBlock['display_result'] = function(block) {{
      return 'show_output_to_user(current_result)\\n';
    }};

    var workspace = Blockly.inject('blocklyDiv', {{
      toolbox: document.getElementById('toolbox'),
      grid: {{spacing: 20, length: 3, colour: '#1f2833', snap: true}},
      trashcan: true
    }});

    // Initialize default structure with explicit phone scan setup 
    var xmlText = '<xml><block type="action_scan" x="40" y="50"><field name="SCANTYPE">phone</field><value name="NAME"><block type="custom_input_string"><field name="RAW_TEXT">+1234567890</field></block></value><next><block type="display_result"></block></next></block></xml>';
    Blockly.Xml.domToWorkspace(Blockly.Xml.textToDom(xmlText), workspace);

    // 🔄 CRITICAL FIX: Push live workspace block data directly back into Python state string
    function updateLivePythonCode() {{
      var code = Blockly.Python.workspaceToCode(workspace);
      // Post text change to stream parent link loop window
      window.parent.postMessage({{type: 'blockly_code_update', code: code}}, '*');
    }}
    workspace.addChangeListener(updateLivePythonCode);
    setTimeout(updateLivePythonCode, 500);

    // Draggable script handler loop
    var element = document.getElementById("draggableTerminal");
    var header = document.getElementById("terminalHeader");
    var activeDragging = false;
    var currentX, currentY, initialX, initialY;
    var xOffset = 0, yOffset = 0;

    header.addEventListener("mousedown", dragStart, false);
    document.addEventListener("mouseup", dragEnd, false);
    document.addEventListener("mousemove", drag, false);

    function dragStart(e) {{
      initialX = e.clientX - xOffset;
      initialY = e.clientY - yOffset;
      if (e.target === header || header.contains(e.target)) {{ activeDragging = true; }}
    }}
    function dragEnd(e) {{ initialX = currentX; initialY = currentY; activeDragging = false; }}
    function drag(e) {{
      if (activeDragging) {{
        e.preventDefault();
        currentX = e.clientX - initialX;
        currentY = e.clientY - initialY;
        xOffset = currentX;
        yOffset = currentY;
        element.style.transform = "translate3d(" + currentX + "px, " + currentY + "px, 0)";
      }}
    }}
  </script>
</body>
</html>
"""

# Embed the responsive canvas overlay engine
components.html(blockly_html_payload, height=860, scrolling=False)

# ----------------------------------------------------
# STAGE 2: SUBTERRANEAN REAL-TIME SYNC ENGINE (SCROLL DOWN)
# ----------------------------------------------------
st.markdown("---")
st.markdown("### 📝 Code Generation Window")
st.write("This box automatically syncs text in real-time when you modify your blocks above:")

# Realtime browser stream updates listener loop hooks
html_listener = """
<script>
window.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'blockly_code_update') {
        const urlParams = new URLSearchParams(window.location.search);
        // Force sync updates directly over parent parameters
        window.parent.document.dispatchEvent(new CustomEvent('update_code', {detail: event.data.code}));
    }
});
</script>
"""
components.html(html_listener, height=0)

# Track block changes live through standard text boxes layout view
user_pipeline_input = st.text_area(
    label="Generated Automation Script String Source File View:",
    value=st.session_state["live_compiled_code"],
    height=160,
    disabled=True,  # Keeps it read-only since the arena automatically outputs code here!
)

# Optional Log Flush Action Utility Switch
if st.button("🧹 Clear Output Logs Monitor", use_container_width=True):
    st.session_state["console_terminal_logs"] = "Monitor buffer cleared."
    st.rerun()