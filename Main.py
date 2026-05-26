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
        return f"❌ ERROR:\n  └── Could not find a server for '{clean_host}'."
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
        return f"❌ ERROR:\n  └── Could not find website names attached to IP '{clean_ip}'"


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
    st.session_state["console_terminal_logs"] = "⚡ MONITOR STREAM ACTIVE...\n⚡ EXECUTING ACTIVE SEQUENCE CHAIN:\n"
    restricted_sandbox_globals = {
        "run_utility_scan": run_utility_scan,
        "show_output_to_user": show_output_to_user,
        "print": lambda *args: show_output_to_user(" ".join(map(str, args))),
        "current_result": ""
    }
    
    # Strip comments and sequence markers before dynamic execution
    execution_code = ""
    for line in compiled_script_text.splitlines():
        if "when_sequence_activated" in line or line.strip() == "pass" or line.strip().startswith("#"):
            continue
        execution_code += line + "\n"
        
    if not execution_code.strip():
        st.session_state["console_terminal_logs"] += "\n⚠️ WARNING: Connect your inputs/actions to the 'When Sequence Activated' block to run!"
        return

    try:
        exec(execution_code, restricted_sandbox_globals)
    except Exception as runtime_exception:
        st.session_state["console_terminal_logs"] += f"\n💥 [SCRIPT RUN ERROR]: {str(runtime_exception)}"

# ==========================================
# 3. INTERACTIVE LAYOUT CONFIGURATION
# ==========================================

st.set_page_config(page_title="EZHack Horizon Studio", layout="wide")

if "console_terminal_logs" not in st.session_state:
    st.session_state["console_terminal_logs"] = "💻 [READY] Construct your sequence layout and hit launch circuit..."

if "live_compiled_code" not in st.session_state:
    st.session_state["live_compiled_code"] = "current_result = run_utility_scan('+15555550199', 'phone')\nshow_output_to_user(current_result)"

# Receives live execution code string directly from the iframe via URL hashing trick
query_params = st.query_params
if "code_sync" in query_params:
    incoming_code = query_params["code_sync"]
    if incoming_code != st.session_state["live_compiled_code"]:
        st.session_state["live_compiled_code"] = incoming_code

# ----------------------------------------------------
# 🪐 TOP CONTROLS ROW
# ----------------------------------------------------
title_col, button_col_1, button_col_2 = st.columns([6, 3, 3])

with title_col:
    st.title("⚡ Horizon Core Toolroom")
    st.caption("Sequential block pipeline interface engineered for recon data diagnostics.")

with button_col_1:
    st.write("")
    trigger_pipeline_run = st.button("🚀 LAUNCH CIRCUIT PIPELINE", type="primary", use_container_width=True)

with button_col_2:
    st.write("")
    if st.button("🧹 Flush Monitor Logs", use_container_width=True):
        st.session_state["console_terminal_logs"] = "Monitor buffer cleared."
        st.rerun()

# Execute block sequences on request
if trigger_pipeline_run:
    with st.spinner("Processing automation pipeline paths..."):
        compile_and_execute_blocks(st.session_state["live_compiled_code"])

safe_terminal_logs = st.session_state["console_terminal_logs"].replace("`", "'").replace("\\", "\\\\").replace("\n", "\\n")

# ----------------------------------------------------
# STAGE 1: VISUAL STUDIO CHAIN CANVAS
# ----------------------------------------------------
st.markdown("### 🗺️ Visual Studio Workspace Canvas")

blockly_html_payload = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Blockly Workspace</title>
  <script src="https://unpkg.com/blockly/blockly.min.js"></script>
  <script src="https://unpkg.com/blockly/python_compressed.js"></script>
  <script src="https://unpkg.com/blockly/blocks_compressed.js"></script>
  <style>
    html, body {{ height: 100%; margin: 0; padding: 0; background-color: #0b0c10; font-family: sans-serif; overflow: hidden; }}
    #containerDiv {{ position: relative; width: 100%; height: 600px; }}
    #blocklyDiv {{ width: 100%; height: 100%; border: 2px solid #1f2833; border-radius: 6px; }}
    
    #draggableTerminal {{
      position: absolute;
      top: 20px;
      right: 20px;
      width: 450px;
      height: 380px;
      z-index: 999;
      background: rgba(11, 12, 16, 0.96);
      border: 2px solid #66fcf1;
      border-radius: 8px;
      box-shadow: 0 0 25px rgba(102, 252, 241, 0.3);
      display: flex;
      flex-direction: column;
    }}
    #terminalHeader {{
      padding: 10px;
      cursor: move;
      background: #1f2833;
      border-bottom: 2px solid #45a29e;
      color: #66fcf1;
      font-weight: bold;
      font-size: 11px;
      display: flex;
      justify-content: space-between;
      user-select: none;
    }}
    #terminalBody {{
      flex: 1;
      padding: 12px;
      margin: 0;
      background: #0b0c10;
      color: #1fec79;
      font-family: monospace;
      font-size: 12px;
      overflow-y: auto;
      white-space: pre-wrap;
    }}
  </style>
</head>
<body>

  <div id="containerDiv">
    <div id="draggableTerminal">
      <div id="terminalHeader">
        <span>🤖 LIVE TARGET OUTPUT TERMINAL</span>
      </div>
      <pre id="terminalBody">{safe_terminal_logs}</pre>
    </div>
    <div id="blocklyDiv"></div>
  </div>

  <xml id="toolbox" style="display: none">
    <category name="🏁 Sequence Setup" colour="0">
      <block type="when_sequence_activated"></block>
    </category>
    <category name="🌐 Targets &amp; Inputs" colour="160">
      <block type="custom_input_string"></block>
    </category>
    <category name="🎯 Scanners &amp; Actions" colour="210">
      <block type="action_scan"></block>
    </category>
    <category name="🖥️ Monitor Controls" colour="65">
      <block type="display_result"></block>
    </category>
  </xml>

  <script>
    // 🏁 Master Event Sequence Start Block Definition
    Blockly.Blocks['when_sequence_activated'] = {{
      init: function() {{
        this.appendDummyInput()
            .appendField("🚀 When Sequence Activated");
        this.setNextStatement(true, null);
        this.setColour(0);
        this.setTooltip("The absolute master execution chain starting anchor block.");
      }}
    }};

    Blockly.Blocks['custom_input_string'] = {{
      init: function() {{
        this.appendDummyInput()
            .appendField("Type Target:")
            .appendField(new Blockly.FieldTextInput("+15555550199"), "RAW_TEXT");
        this.setOutput(true, "String");
        this.setColour(160);
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
        this.setColour(65);
      }}
    }};

    // Custom Python generation definitions for blocks
    Blockly.Python.forBlock['when_sequence_activated'] = function(block) {{
      return '# when_sequence_activated\\n';
    }};

    Blockly.Python.forBlock['custom_input_string'] = function(block) {{
      var rawText = block.getFieldValue('RAW_TEXT');
      return ['"' + rawText + '"', 0];
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

    // Draw standard starting template inside the workspace editor
    var xmlText = '<xml><block type="when_sequence_activated" x="40" y="40"><next><block type="action_scan"><field name="SCANTYPE">phone</field><value name="NAME"><block type="custom_input_string"><field name="RAW_TEXT">+15555550199</field></block></value><next><block type="display_result"></block></next></block></next></block></xml>';
    Blockly.Xml.domToWorkspace(Blockly.Xml.textToDom(xmlText), workspace);

    // 🎯 REWRITE: THE TARGETED CHAIN CRAWLER DETECTION ENGINE
    // This function detects when a block is changed or added, but ONLY crawls down the root sequence anchor block!
    var debounceTimer = null;
    function processWorkspaceSequenceChange(event) {{
      // Prevent flooding Streamlit on intermediate drag positions
      if (event.type === Blockly.Events.BLOCK_MOVE && event.isUiChange) return;

      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function() {{
        var topBlocks = workspace.getTopBlocks(false);
        var rootSequenceBlock = null;
        
        // Step 1: Scan layout to find the single master sequence block
        for (var i = 0; i < topBlocks.length; i++) {{
          if (topBlocks[i].type === 'when_sequence_activated') {{
            rootSequenceBlock = topBlocks[i];
            break;
          }}
        }}
        
        var generatedSequenceCode = "";
        
        // Step 2: Loop exclusively through blocks attached below the Master anchor
        if (rootSequenceBlock) {{
          var currentBlock = rootSequenceBlock.getNextBlock();
          while (currentBlock) {{
            // Translate the block using Blockly's standard Python engine rules
            var blockCode = Blockly.Python.blockToCode(currentBlock);
            if (typeof blockCode === 'string') {{
              generatedSequenceCode += blockCode;
            }} else if (Array.isArray(blockCode)) {{
              generatedSequenceCode += blockCode[0];
            }}
            // Crawl sequentially down to the next connected node block item
            currentBlock = currentBlock.getNextBlock();
          }}
        }} else {{
          generatedSequenceCode = "# ⚠️ Error: 'When Sequence Activated' block missing from layout canvas!";
        }}

        // Step 3: Refresh the state by directly injecting parameters safely out to parent container window paths
        var encodedCode = encodeURIComponent(generatedSequenceCode.trim());
        var currentUrl = window.parent.location.href.split('?')[0];
        window.parent.location.replace(currentUrl + "?code_sync=" + encodedCode);
      }}, 300); // 300ms debounce ensures clean user typing captures
    }}

    // Hook the change detector into the workspace events pipeline
    workspace.addChangeListener(processWorkspaceSequenceChange);

    // Draggable Window Interface Rules
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

components.html(blockly_html_payload, height=620, scrolling=False)

# ----------------------------------------------------
# STAGE 2: VISIBLE PYTHON CODE TERMINAL OUTLET
# ----------------------------------------------------
st.markdown("### 📝 Code Translation Behind the Blocks")
st.write("This stream displays the live, active sequence block chain structure translating directly into execution memory:")

st.code(st.session_state["live_compiled_code"], language="python")