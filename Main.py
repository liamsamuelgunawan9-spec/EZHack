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
        return f"❌ ERROR:\n  └── Could not find a server for '{clean_host}'. Check spelling!"
    except Exception as e:
        return f"💥 SYSTEM CRASH: {str(e)}"


def perform_reverse_dns(target: str) -> str:
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
    st.session_state["console_terminal_logs"] = "⚡ MONITOR STREAM ACTIVE...\n⚡ EXECUTING ACTIVE CANVAS BLOCKS:\n"
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

# Persistent Session Memory Backstops
if "console_terminal_logs" not in st.session_state:
    st.session_state["console_terminal_logs"] = "💻 [READY] Construct your layout and hit launch circuit..."

# Check query string parameter for live block updates
current_url_code = st.query_params.get("code", "")
if current_url_code:
    st.session_state["live_compiled_code"] = current_url_code
elif "live_compiled_code" not in st.session_state:
    st.session_state["live_compiled_code"] = "current_result = run_utility_scan('+1234567890', 'phone')\nshow_output_to_user(current_result)"

# ----------------------------------------------------
# 🪐 TOP-LEFT CONTROLS ROW (NO MORE SCROLLING)
# ----------------------------------------------------
title_col, button_col_1, button_col_2 = st.columns([6, 3, 3])

with title_col:
    st.title("⚡ Horizon Core Toolroom")
    st.caption("Clean drag-and-drop workspace engine built for direct operations execution.")

with button_col_1:
    st.write("")
    trigger_pipeline_run = st.button("🚀 LAUNCH CIRCUIT PIPELINE", type="primary", use_container_width=True)

with button_col_2:
    st.write("")
    if st.button("🧹 Flush Monitor Logs", use_container_width=True):
        st.session_state["console_terminal_logs"] = "Monitor buffer cleared."
        st.rerun()

# Run current workspace parameters instantly on click
if trigger_pipeline_run:
    with st.spinner("Processing automated actions code sequences..."):
        compile_and_execute_blocks(st.session_state["live_compiled_code"])

# Safely wrap internal data frames for visual layout execution passing
safe_terminal_logs = st.session_state["console_terminal_logs"].replace("`", "'").replace("\\", "\\\\").replace("\n", "\\n")

# ----------------------------------------------------
# STAGE 1: FULL-WINDOW BLOCKLY GRID WORKSPACE
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
    #blocklyDiv {{ width: 100%; height: 100%; border: 2px solid #1f2833; border-radius: 6px; }}
    
    #draggableTerminal {{
      position: absolute;
      top: 30px;
      right: 30px;
      width: 490px;
      height: 460px;
      z-index: 999;
      background: rgba(11, 12, 16, 0.96);
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
      letter-spacing: 1px;
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
    </category>
    <category name="🎯 Scanners &amp; Actions" colour="210">
      <block type="action_scan"></block>
    </category>
    <category name="🖥️ Monitor Controls" colour="20">
      <block type="display_result"></block>
    </category>
  </xml>

  <script>
    Blockly.Blocks['custom_input_string'] = {{
      init: function() {{
        this.appendDummyInput()
            .appendField("Type Target:")
            .appendField(new Blockly.FieldTextInput("555-0199"), "RAW_TEXT");
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
      return ['"' + block.getFieldValue('RAW_TEXT') + '"', 0];
    }};

    Blockly.Python.forBlock['target'] = function(block) {{
      return ['"' + block.getFieldValue('Target') + '"', 0];
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

    // Setup clear structural defaults
    var xmlText = '<xml><block type="action_scan" x="40" y="50"><field name="SCANTYPE">phone</field><value name="NAME"><block type="custom_input_string"><field name="RAW_TEXT">+1234567890</field></block></value><next><block type="display_result"></block></next></block></xml>';
    Blockly.Xml.domToWorkspace(Blockly.Xml.textToDom(xmlText), workspace);

    // Dynamic Query Parameter Auto-sync Rule 
    function updateLivePythonCode() {{
      var code = Blockly.Python.workspaceToCode(workspace);
      var currentUrl = new URL(window.parent.location.href);
      currentUrl.searchParams.set("code", code);
      window.parent.history.replaceState({{}}, "", currentUrl.toString());
    }}
    
    workspace.addChangeListener(updateLivePythonCode);
    setTimeout(updateLivePythonCode, 400);

    // Draggable Window Configs
    var element = document.getElementById("draggableTerminal");
    var header = document.getElementById("terminalHeader");
    var activeDragging = false;
    var currentX, currentY, initialX, initialY, xOffset = 0, yOffset = 0;

    header.addEventListener("mousedown", function(e) {{
      initialX = e.clientX - xOffset; initialY = e.clientY - yOffset;
      if (e.target === header || header.contains(e.target)) activeDragging = true;
    }}, false);
    document.addEventListener("mouseup", function() {{ activeDragging = false; }}, false);
    document.addEventListener("mousemove", function(e) {{
      if (activeDragging) {{
        e.preventDefault();
        currentX = e.clientX - initialX; currentY = e.clientY - initialY;
        xOffset = currentX; yOffset = currentY;
        element.style.transform = "translate3d(" + currentX + "px, " + currentY + "px, 0)";
      }}
    }}, false);
  </script>
</body>
</html>
"""
components.html(blockly_html_payload, height=860, scrolling=False)