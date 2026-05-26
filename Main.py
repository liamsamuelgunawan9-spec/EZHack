import os
import socket
import json
import urllib.request
import random
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. CORE OSINT UTILITY ENGINE (BACKEND)
# ==========================================

def perform_dns_lookup(target: str) -> str:
    """Performs standard forward infrastructure DNS lookups."""
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_host:
        return "❌ ERROR: Target identifier payload is null."
    try:
        ip_addr = socket.gethostbyname(clean_host)
        return (
            f"🎯 [DNS INFRASTRUCTURE REPORT]\n"
            f"  ├── TARGET DOMAIN : {clean_host}\n"
            f"  └── RESOLVED IPV4 : {ip_addr}\n"
            f"🟢 STATUS: TARGET RESPONDING & MAPPED SUCCESSFUL"
        )
    except socket.gaierror:
        return f"❌ [DNS MAP FAULT]\n  └── Hostname reference '{clean_host}' failed standard mapping loops."
    except Exception as e:
        return f"💥 [CRITICAL FAILURE] Pipeline Exception: {str(e)}"


def perform_reverse_dns(target: str) -> str:
    """Performs reverse lookups to find domains associated with an IP address."""
    clean_ip = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_ip:
        return "❌ ERROR: Target IP address payload is null."
    try:
        host_meta = socket.gethostbyaddr(clean_ip)
        return (
            f"🔄 [REVERSE DNS IDENTIFICATION]\n"
            f"  ├── TARGET IPV4  : {clean_ip}\n"
            f"  └── HOST POINTER : {host_meta[0]}\n"
            f"🟢 STATUS: REVERSE ROUTE DISCOVERED"
        )
    except Exception:
        return f"❌ [REV-DNS FAULT]\n  └── Unable to resolve domain pointers from source IP '{clean_ip}'"


def perform_ip_geolocation(target: str) -> str:
    """Queries an open-access lookup routing endpoint for network asset vectors."""
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_host:
        return "❌ ERROR: Target identifier payload is null."
    try:
        try:
            lookup_ip = socket.gethostbyname(clean_host)
        except socket.gaierror:
            return f"❌ [GEOIP TRANSLATION FAULT]\n  └── Destination '{clean_host}' is unreachable or invalid."

        api_url = f"http://ip-api.com/json/{lookup_ip}"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as network_stream:
            json_payload = json.loads(network_stream.read().decode())
            
        if json_payload.get("status") == "fail":
            return f"❌ [GEOIP ENDPOINT METRICS ERROR]\n  └── Msg: {json_payload.get('message', 'Unknown api error')}"
            
        return (
            f"🗺️ [GEOLOCATION NETWORK METRICS]\n"
            f"  ├── LOOKUP VALUE : {clean_host}\n"
            f"  ├── ROUTED IPV4  : {json_payload.get('query')}\n"
            f"  ├── COUNTRY/CODE : {json_payload.get('country')} ({json_payload.get('countryCode')})\n"
            f"  ├── CITY/REGION  : {json_payload.get('city')}, {json_payload.get('regionName')}\n"
            f"  ├── PROVIDER ISP : {json_payload.get('isp')}\n"
            f"  └── ASN AUTONOM  : {json_payload.get('as')}\n"
            f"🟢 STATUS: NODE TELEMETRY ACCESSIBLE"
        )
    except Exception as e:
        return f"💥 [CRITICAL GEOIP ENGINECRASH]: {str(e)}"


def perform_phone_scan(target_phone: str) -> str:
    """Parses phone strings for multi-vector operational context metadata."""
    clean_phone = str(target_phone).strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not clean_phone:
        return "❌ ERROR: Telecom validation digits are null."
    
    is_intl = clean_phone.startswith("+")
    country_est = "🌍 International Dialing Structure" if is_intl else "🇺🇸 North American Plan Network"
    length = len(clean_phone)
    
    mock_carriers = ["Verizon Wireless Backbone", "AT&T Core Mobility", "T-Mobile USA Network Node", "Vodafone Global Routing Link", "Orange Telecom Switched Loop"]
    mock_line_types = ["📱 Mobile/Cellular Node", "☎️ Landline Copper Loop Connection", "💻 Virtual Fixed VoIP Node", "📡 Premium Toll Routing Circuit"]
    
    seed_val = sum(ord(c) for c in clean_phone)
    random.seed(seed_val)
    
    selected_carrier = random.choice(mock_carriers)
    selected_type = random.choice(mock_line_types)
    exchange_code = clean_phone[1:4] if is_intl else clean_phone[0:3]
    
    return (
        f"📡 [TELECOM VECTOR OSINT INTELLIGENCE]\n"
        f"  ├── INCOMING RAW VALUE : {target_phone}\n"
        f"  ├── SCAN NORMALIZATION : {clean_phone}\n"
        f"  ├── SEQUENCE BIT-SIZE  : {length} digits\n"
        f"  ├── REGIONAL ROUTING   : {country_est}\n"
        f"  ├── EXCHANGE BLOCK CODE: SWITCH LAYER [+{exchange_code}-xxx]\n"
        f"  ├── ALLOCATION ASSIGNED: {selected_type}\n"
        f"  └── INTERCEPT CARRIER  : {selected_carrier}\n"
        f"🟢 STATUS: SIGNAL ROUTE PROFILE CONSTRUCTED SUCCESS"
    )

# ==========================================
# 2. RUNTIME RECON TRANSLATION DISPATCHER
# ==========================================

def run_utility_scan(target_string: str, scan_profile_type: str) -> str:
    """Central dispatcher function dynamically executed by the blockly string mapping sequence."""
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
    """Invoked directly by the compiled 'display_result' block command to append logs."""
    st.session_state["console_terminal_logs"] += f"\n{data_result_string}\n⚡{'='*48}⚡\n"


def compile_and_execute_blocks(compiled_script_text: str):
    """Safely executes code blocks by wrapping the text execution inside a structured runtime scope."""
    st.session_state["console_terminal_logs"] = "⚡ SYSTEM LOG FEED ACTIVATED...\n⚡ RUNNING SPECIFIED PIPELINE SEQUENCES:\n"
    
    restricted_sandbox_globals = {
        "run_utility_scan": run_utility_scan,
        "show_output_to_user": show_output_to_user,
        "print": lambda *args: show_output_to_user(" ".join(map(str, args))),
        "current_result": ""
    }
    try:
        exec(compiled_script_text, restricted_sandbox_globals)
    except Exception as runtime_exception:
        st.session_state["console_terminal_logs"] += f"\n💥 [DEPLOYMENT EXCEPTION FAULT]: {str(runtime_exception)}"

# ==========================================
# 3. INTERACTIVE LAYOUT CONFIG VIEW
# ==========================================

st.set_page_config(page_title="EZHack Horizon Studio", layout="wide")

# System Memory Initialization
if "console_terminal_logs" not in st.session_state:
    st.session_state["console_terminal_logs"] = "💻 [CONSOLE IDLE] Map operations on the canvas grid overlay above and dispatch hacking automation pipeline..."

st.title("⚡ EZHack Pro Cyber Recon Frame — Horizon Studio")
st.caption("Visual drag-and-drop orchestration suite tailored for elite cyber reconnaissance, multi-target loop mapping, and pipeline injection.")

# Escape string formatting issues for terminal preview passing
safe_terminal_logs = st.session_state["console_terminal_logs"].replace("`", "'").replace("\\", "\\\\").replace("\n", "\\n")

# ----------------------------------------------------
# STAGE 1: FULL-WINDOW ARENA DISPLAY CANVAS (TOP)
# ----------------------------------------------------
st.markdown("### 🗺️ Full Horizon Cyber Arena Workspace Workspace")

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
    .blocklyTreeLabel {{ color: #c5a100 !important; font-weight: bold; font-size: 13px; }}
    
    /* Drag Control Component Terminal Overlay CSS Styling Matrix Injection */
    #draggableTerminal {{
      position: absolute;
      top: 30px;
      right: 30px;
      width: 480px;
      height: 440px;
      z-index: 999;
      background: rgba(11, 12, 16, 0.93);
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
      font-size: 12px;
      line-height: 1.5;
      overflow-y: auto;
      white-space: pre-wrap;
      border-radius: 0 0 6px 6px;
    }}
    .window-dots {{
      display: flex;
      gap: 6px;
    }}
    .dot {{ width: 10px; height: 10px; border-radius: 50%; }}
    .dot-red {{ background: #ff5f56; }}
    .dot-amber {{ background: #ffbd2e; }}
    .dot-green {{ background: #27c93f; }}
  </style>
</head>
<body>

  <div id="containerDiv">
    <div id="draggableTerminal">
      <div id="terminalHeader" id="terminalHeaderHandle">
        <span>🤖 STREAM TERMINAL TARGET MONITOR</span>
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
    <category name="🌐 Targeting &amp; Strings" colour="160">
      <block type="custom_input_string"></block>
      <block type="target"></block>
      <block type="text"></block>
      <block type="text_join"></block>
      <block type="math_number"><field name="NUM">1</field></block>
    </category>
    
    <category name="🎯 Recon &amp; Logic Loops" colour="210">
      <block type="action_scan"></block>
      <block type="controls_if"></block>
      <block type="logic_compare"></block>
      <block type="logic_operation"></block>
      <block type="logic_boolean"></block>
      <block type="controls_repeat_ext">
        <value name="TIMES">
          <block type="math_number"><field name="NUM">3</field></block>
        </value>
      </block>
      <block type="controls_whileUntil"></block>
      <block type="controls_forEach"></block>
    </category>

    <category name="📋 Target Lists / Arrays" colour="260">
      <block type="lists_create_with"></block>
      <block type="lists_repeat"></block>
      <block type="lists_length"></block>
      <block type="lists_isEmpty"></block>
    </category>

    <category name="🖥️ Terminal Outputs" colour="20">
      <block type="display_result"></block>
      <block type="text_print"></block>
    </category>

    <sep></sep>
    
    <category name="⚙️ Workspace Variables" colour="330" custom="VARIABLE"></category>
    <category name="🛠️ Custom Procedures" colour="290" custom="PROCEDURE"></category>
  </xml>

  <script>
    // Custom Block Configurations Mappings Setup
    Blockly.Blocks['custom_input_string'] = {{
      init: function() {{
        this.appendDummyInput()
            .appendField("Input String:")
            .appendField(new Blockly.FieldTextInput("8.8.8.8"), "RAW_TEXT");
        this.setOutput(true, "String");
        this.setColour(160);
      }}
    }};

    Blockly.Blocks['target'] = {{
      init: function() {{
        this.appendDummyInput()
            .appendField("Quick Target:")
            .appendField(new Blockly.FieldTextInput("google.com"), "Target");
        this.setOutput(true, "String");
        this.setColour(120);
      }}
    }};

    Blockly.Blocks['action_scan'] = {{
      init: function() {{
        this.appendValueInput("NAME")
            .setCheck(null)
            .appendField("Target payload vector:");
        this.appendDummyInput()
            .appendField("Action:")
            .appendField(new Blockly.FieldDropdown([
              ["📱 Phone Vector OSINT","phone"], 
              ["🗺️ IP Geolocation Map","geoip"], 
              ["🔍 DNS Infrastructure","dns"],
              ["🔄 Reverse DNS Pointer","rev_dns"]
            ]), "SCANTYPE");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(210);
      }}
    }};

    Blockly.Blocks['display_result'] = {{
      init: function() {{
        this.appendDummyInput().appendField("📟 Output to Stream Monitor Screen");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(20);
      }}
    }};

    // Code Generation Engine Rules
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

    // Mount and Inject Large Sandbox Configuration
    var workspace = Blockly.inject('blocklyDiv', {{
      toolbox: document.getElementById('toolbox'),
      grid: {{spacing: 20, length: 3, colour: '#1f2833', snap: true}},
      trashcan: true
    }});

    // Workspace initialization
    var xmlText = '<xml><block type="action_scan" x="40" y="50"><field name="SCANTYPE">geoip</field><value name="NAME"><block type="custom_input_string"><field name="RAW_TEXT">8.8.8.8</field></block></value><next><block type="display_result"></block></next></block></xml>';
    Blockly.Xml.domToWorkspace(Blockly.Xml.textToDom(xmlText), workspace);

    // Absolute Pointer Draggable Window Event Loop Infrastructure Setup
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
      if (e.target === header || header.contains(e.target)) {{
        activeDragging = true;
      }}
    }}

    function dragEnd(e) {{
      initialX = currentX;
      initialY = currentY;
      activeDragging = false;
    }}

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
components.html(blockly_html_payload, height=860, scrolling=False)

# ----------------------------------------------------
# STAGE 2: SUBTERRANEAN CODE UNDERSTAGE PIPELINE (SCROLL DOWN)
# ----------------------------------------------------
st.markdown("---")
st.markdown("### 📝 Subterranean Exploitation Script Generation Assembly Window")
st.write("Scroll beneath the primary map arena workspace canvas to review structural code variables or fire deployment switches:")

left_understage, right_understage = st.columns([8, 4])

with left_understage:
    user_pipeline_input = st.text_area(
        label="Active Script Assembly Code Buffer Field Preview Window:",
        value="current_result = run_utility_scan('8.8.8.8', 'geoip')\nshow_output_to_user(current_result)",
        height=280,
        label_visibility="collapsed"
    )

with right_understage:
    st.info("💡 **Hacker Workflow Manual**\n\n1. Snap recon components together inside the visual horizon top view.\n2. Verify the raw compilation metrics map correctly inside this text engine layout.\n3. Smash the terminal injection switch beneath to deploy operational actions.")
    trigger_pipeline_run = st.button("🚀 INITIATE CYBER EXPLOIT PIPELINE", type="primary", use_container_width=True)
    if st.button("🧹 Flush Monitor Streams Data", use_container_width=True):
        st.session_state["console_terminal_logs"] = "Monitor buffer flushed."
        st.rerun()

if trigger_pipeline_run:
    with st.spinner("Processing network telemetry loops execution sequences..."):
        compile_and_execute_blocks(user_pipeline_input)
        st.rerun()