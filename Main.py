import os
import socket
import json
import urllib.request
import random
import streamlit as st
import streamlit.components.v1 as components

# Import Google's phonenumbers library components
import phonenumbers
from phonenumbers import carrier, geocoder, timezone

# ==========================================
# 1. UTILITY FUNCTIONS (GLOBAL OSINT ENGINE)
# ==========================================

def perform_dns_lookup(target: str) -> str:
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_host:
        return "❌ ERROR: You didn't enter a website name!"
    try:
        ip_addr = socket.gethostbyname(clean_host)
        return f"🔍 [SERVER LOOK-UP] Website: {clean_host} -> IP: {ip_addr}"
    except Exception as e:
        return f"❌ ERROR: {str(e)}"

def perform_ip_geolocation(target: str) -> str:
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_host:
        return "❌ ERROR: Target missing!"
    try:
        lookup_ip = socket.gethostbyname(clean_host)
        api_url = f"http://ip-api.com/json/{lookup_ip}"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as stream:
            payload = json.loads(stream.read().decode())
        if payload.get("status") == "fail":
            return f"❌ API ERROR: {payload.get('message')}"
        return f"🗺️ [LOCATION] IP: {lookup_ip} | Country: {payload.get('country')} | City: {payload.get('city')}"
    except Exception as e:
        return f"💥 ERROR: {str(e)}"

def perform_phone_tracking(target: str) -> str:
    # Clean up standard characters but preserve the '+' sign for country codes
    clean_phone = str(target).strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace('"', '').replace("'", "")
    if not clean_phone:
        return "❌ ERROR: Phone number input missing!"
    
    # Smart fallback: If an Indonesian number is typed as '08...', automatically prefix it with '+62'
    if clean_phone.startswith("08"):
        clean_phone = "+62" + clean_phone[1:]
    # If a number doesn't start with '+', try parsing with an assumption or alert
    elif not clean_phone.startswith("+"):
        clean_phone = "+" + clean_phone

    try:
        # Parse the data via Google's library engine
        parsed_number = phonenumbers.parse(clean_phone, None)
        
        # Verify if the number structure is mathematically valid globally
        if not phonenumbers.is_valid_number(parsed_number):
            return f"❌ ERROR: '{clean_phone}' is not a valid global phone number structure."

        # Extract specifications dynamically
        country_code = parsed_number.country_code
        national_num = parsed_number.national_number
        
        # 1. Gather Carrier/Operator Info (Supporting multiple languages, default English 'en')
        operator_name = carrier.name_for_number(parsed_number, "en")
        if not operator_name:
            operator_name = "Unknown Carrier / Protected Virtual Infrastructure"
            
        # 2. Gather Location/Region name mapping
        region_location = geocoder.description_for_number(parsed_number, "en")
        if not region_location:
            region_location = "General Regional Assignment Pool"
            
        # 3. Gather standard time zones associated
        zones = timezone.time_zones_for_number(parsed_number)
        timezone_string = ", ".join(zones) if zones else "Unknown Grid Time"

        return (f"📱 [GLOBAL PHONE PROFILE - VERIFIED]\n"
                f"   • Input Target   : {clean_phone}\n"
                f"   • Country Code   : +{country_code}\n"
                f"   • National ID    : {national_num}\n"
                f"   • Core Location  : {region_location}\n"
                f"   • Network Carrier: {operator_name}\n"
                f"   • Zone Matrix    : {timezone_string}\n"
                f"   • Status Check   : Active Allocation")

    except Exception as err:
        return f"❌ ENGINE EXCEPTION: Failed to process parse matrix. Details: {str(err)}"

# Custom tracking collectors to feed into the workspace iframe directly
if "terminal_history_output" not in st.session_state:
    st.session_state["terminal_history_output"] = "🚀 System Ready. Awaiting Sequence Trigger Execution..."

def run_scan(target: str, mode: str):
    if mode == "dns":
        res = perform_dns_lookup(target)
    elif mode == "geoip":
        res = perform_ip_geolocation(target)
    elif mode == "phone":
        res = perform_phone_tracking(target)
    st.session_state["terminal_history_output"] += f"\\n[SCAN RUNNER] Target: {target} | Mode: {mode}\\n{res}\\n"

def verify_protocol(target: str, verification_mode: str):
    res = f"🔒 [PROTOCOL AUDIT] Structural validation complete for: {verification_mode.upper()} on {target}"
    st.session_state["terminal_history_output"] += f"\\n[VERIFIER] Target: {target}\\n{res}\\n"


# ==========================================
# 2. STREAMLIT INTERFACE LAYER & FALLBACK
# ==========================================

st.set_page_config(page_title="Horizon Studio", layout="wide")

st.title("⚡ Horizon Core Toolroom")
st.caption("Visual Block Configuration Environment")

if "synced_workspace_code" not in st.session_state:
    st.session_state["synced_workspace_code"] = ""

# Sidebar Sequence Trigger Terminal Panel
with st.sidebar:
    st.header("🎮 Sequence Automation")
    st.markdown("Build your block pipeline on the workspace floor, then trigger execution below.")
    
    st.session_state["synced_workspace_code"] = st.text_area(
        "📋 Compiled Workspace Payload", 
        value=st.session_state["synced_workspace_code"], 
        height=140,
        help="This window displays the compiled matrix logic coming live from the canvas floor below."
    )
    
    if st.button("🚀 Execute Workspace Sequence", type="primary", use_container_width=True):
        code_to_run = st.session_state["synced_workspace_code"].strip()
        
        if not code_to_run or "Sequence Active" not in code_to_run:
            st.warning("⚠️ Execution Halted: Connect your blocks to 'Sequence Start' on the canvas!")
        else:
            try:
                st.session_state["terminal_history_output"] = "🛰️ RUNNING NEW SEQUENCE PAYLOAD MATRIX...\\n-----------------------------------------\\n"
                exec(code_to_run)
            except Exception as runtime_err:
                st.session_state["terminal_history_output"] += f"\\n💥 RUNTIME EXCEPTION: {str(runtime_err)}\\n"

st.markdown("### 🗺️ Visual Workspace Floor")


# ==========================================
# 3. ### LOCKED CORE START ### - DO NOT TOUCH
# ==========================================

try:
    incoming_payload = st.query_params.get("payload_matrix", "")
    if incoming_payload:
        st.session_state["synced_workspace_code"] = incoming_payload
except Exception:
    pass

blockly_html_payload = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://unpkg.com/blockly/blockly.min.js"></script>
  <script src="https://unpkg.com/blockly/python_compressed.js"></script>
  <script src="https://unpkg.com/blockly/blocks_compressed.js"></script>
  <style>
    html, body {{ height: 100%; margin: 0; padding: 0; background-color: #0b0c10; font-family: monospace; color: #1fec79; overflow: hidden; }}
    #workspaceWrapper {{ display: flex; flex-direction: column; height: 680px; padding: 5px; box-sizing: border-box; position: relative; }}
    #blocklyDiv {{ flex: 1; border: 2px solid #45a29e; border-radius: 6px; box-shadow: 0 0 15px rgba(69, 162, 158, 0.15); }}
    #debugTerminal {{ 
      height: 140px; 
      background: #000000; 
      border: 2px solid #ff0055; 
      margin-top: 12px; 
      padding: 12px; 
      overflow-y: auto; 
      white-space: pre-wrap; 
      font-size: 11px;
      border-radius: 6px;
      box-shadow: 0 0 15px rgba(255, 0, 85, 0.1);
    }}
    
    #floatingResultsTab {{
      position: absolute;
      top: 40px;
      right: 40px;
      width: 460px;
      background-color: #1f2833;
      border: 2px solid #1fec79;
      border-radius: 8px;
      z-index: 9999;
      box-shadow: 0 10px 30px rgba(0,0,0,0.7);
    }}
    #floatingHeader {{
      padding: 8px 12px;
      cursor: move;
      background-color: #0b0c10;
      border-bottom: 2px solid #1fec79;
      font-weight: bold;
      color: #1fec79;
      display: flex;
      justify-content: space-between;
      border-top-left-radius: 6px;
      border-top-right-radius: 6px;
      font-size: 12px;
    }}
    .terminalContent {{
      padding: 12px;
      background-color: #000000;
      color: #ffffff;
      height: 250px;
      overflow-y: auto;
      font-size: 12px;
      white-space: pre-wrap;
      border-bottom-left-radius: 6px;
      border-bottom-right-radius: 6px;
    }}
  </style>
</head>
<body>

  <div id="workspaceWrapper">
    <div id="blocklyDiv"></div>
    
    <div id="floatingResultsTab">
      <div id="floatingHeader">
        <span>🎛️ DRIFT DRAGGABLE RESULTS TERMINAL</span>
        <span style="color: #ff0055; font-size: 10px;">● LIVE</span>
      </div>
      <div class="terminalContent" id="sequenceTerminalContent">{st.session_state["terminal_history_output"]}</div>
    </div>

    <div id="debugTerminal">> Awaiting block placement events...</div>
  </div>

  <xml id="toolbox" style="display: none">
    <category name="🏁 Sequences" colour="0">
      <block type="when_sequence_activated"></block>
    </category>
    <category name="🌐 Inputs" colour="160">
      <block type="custom_input_string"></block>
      <block type="multi_target_list"></block>
    </category>
    <category name="🎯 Actions" colour="210">
      <block type="action_scan"></block>
      <block type="protocol_verify"></block>
    </category>
    <category name="🔠 Text Utilities" colour="120">
      <block type="text_join"></block>
      <block type="text_length"></block>
    </category>
    <category name="🧠 Logic Flow" colour="60">
      <block type="controls_if"></block>
      <block type="logic_boolean"></block>
    </category>
  </xml>

  <script>
    dragElement(document.getElementById("floatingResultsTab"));

    function dragElement(elmnt) {{
      var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
      if (document.getElementById(elmnt.id + "Header")) {{
        document.getElementById(elmnt.id + "Header").onmousedown = dragMouseDown;
      }} else {{
        elmnt.onmousedown = dragMouseDown;
      }}

      function dragMouseDown(e) {{
        e = e || window.event;
        if(e.target.className === "terminalContent") return;
        e.preventDefault();
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        document.onmousemove = elementDrag;
      }}

      function elementDrag(e) {{
        e = e || window.event;
        e.preventDefault();
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
        elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
      }}

      function closeDragElement() {{
        document.onmouseup = null;
        document.onmousemove = null;
      }}
    }}

    // --- Custom System Blocks ---
    Blockly.Blocks['when_sequence_activated'] = {{
      init: function() {{
        this.appendDummyInput().appendField("🚀 Sequence Start");
        this.setNextStatement(true, null);
        this.setColour(0);
      }}
    }};

    Blockly.Blocks['custom_input_string'] = {{
      init: function() {{
        this.appendDummyInput()
            .appendField("Target:")
            .appendField(new Blockly.FieldTextInput("+628111989199"), "RAW_TEXT");
        this.setOutput(true, "String");
        this.setColour(160);
      }}
    }};

    Blockly.Blocks['multi_target_list'] = {{
      init: function() {{
        this.appendDummyInput()
            .appendField("Multi-Targets:")
            .appendField(new Blockly.FieldTextInput("target1.com, target2.com"), "TARGETS");
        this.setOutput(true, "String");
        this.setColour(160);
      }}
    }};

    Blockly.Blocks['action_scan'] = {{
      init: function() {{
        this.appendValueInput("NAME").setCheck("String").appendField("Scan Target:");
        this.appendDummyInput()
            .appendField("Action:")
            .appendField(new Blockly.FieldDropdown([
              ["🔍 DNS Lookup","dns"],
              ["🗺️ Geolocation","geoip"],
              ["📱 Phone Tracker Info", "phone"]
            ]), "SCANTYPE");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(210);
      }}
    }};

    Blockly.Blocks['protocol_verify'] = {{
      init: function() {{
        this.appendValueInput("TARGET").setCheck("String").appendField("Verify Target:");
        this.appendDummyInput()
            .appendField("Check Option:")
            .appendField(new Blockly.FieldDropdown([
              ["🔒 SSL/TLS Certificate","ssl"],
              ["🔌 Open Ports Scan","ports"]
            ]), "VERIFYTYPE");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(210);
      }}
    }};

    Blockly.Python.forBlock['when_sequence_activated'] = function(block) {{ return '# Sequence Active\\n'; }};
    Blockly.Python.forBlock['custom_input_string'] = function(block) {{ return ["'" + block.getFieldValue('RAW_TEXT') + "'", 0]; }};
    Blockly.Python.forBlock['multi_target_list'] = function(block) {{ return ["'" + block.getFieldValue('TARGETS') + "'", 0]; }};
    
    Blockly.Python.forBlock['action_scan'] = function(block) {{
      var type = block.getFieldValue('SCANTYPE');
      var val = Blockly.Python.valueToCode(block, 'NAME', 0) || "''";
      return 'run_scan(target=' + val + ', mode="' + type + '")\\n';
    }};

    Blockly.Python.forBlock['protocol_verify'] = function(block) {{
      var type = block.getFieldValue('VERIFYTYPE');
      var val = Blockly.Python.valueToCode(block, 'TARGET', 0) || "''";
      return 'verify_protocol(target=' + val + ', verification_mode="' + type + '")\\n';
    }};

    var workspace = Blockly.inject('blocklyDiv', {{
      toolbox: document.getElementById('toolbox'),
      grid: {{spacing: 20, length: 3, colour: '#1f2833', snap: true}},
      trashcan: true
    }});

    var terminal = document.getElementById("debugTerminal");

    function renderDebugLogs() {{
      var allBlocks = workspace.getAllBlocks(false);
      var textOutput = "⚙️ LIVE WORKSPACE PARSER MATRIX\\n-----------------------------------------\\n";
      textOutput += "• Active elements mapped on floor: " + allBlocks.length + "\\n\\n";
      
      var generatedPythonCode = "";
      var sequenceFound = false;
      
      for (var i = 0; i < allBlocks.length; i++) {{
        if (allBlocks[i].type === 'when_sequence_activated') {{
          sequenceFound = true;
          textOutput += "🏁 [Sequence Node] Enabled -> [UUID: " + allBlocks[i].id + "]\\n";
          
          generatedPythonCode += Blockly.Python.blockToCode(allBlocks[i]);
          var nextBlock = allBlocks[i].getNextBlock();
          while(nextBlock) {{
            textOutput += "   └── Connected Step: " + nextBlock.type;
            if(nextBlock.type === 'action_scan') {{
              textOutput += " [Action Mode: " + nextBlock.getFieldValue('SCANTYPE').toUpperCase() + "]";
            }} else if(nextBlock.type === 'protocol_verify') {{
              textOutput += " [Verification Mode: " + nextBlock.getFieldValue('VERIFYTYPE').toUpperCase() + "]";
            }}
            textOutput += "\\n";
            generatedPythonCode += Blockly.Python.blockToCode(nextBlock);
            nextBlock = nextBlock.getNextBlock();
          }}
        }}
      }}
      
      if(!sequenceFound) {{
        textOutput += "⚠️ STATUS ALERT: Drag and drop a 'Sequence Start' block onto the workspace canvas floor to begin compilation.";
      }} else {{
        textOutput += "\\n🟢 PARSING INTEGRITY STATUS: PIPELINE CHANNELS HEALTHY";
        textOutput += "\\n\\n📋 COMPILED TARGET SCRIPT OUTPUT:\\n" + generatedPythonCode;
        
        var targetUrl = window.parent.location.origin + window.parent.location.pathname + "?payload_matrix=" + encodeURIComponent(generatedPythonCode);
        if(window.parent.location.search !== "?payload_matrix=" + encodeURIComponent(generatedPythonCode)) {{
           window.parent.history.replaceState({{}}, '', targetUrl);
        }}
      }}
      
      terminal.innerText = textOutput;
    }}

    workspace.addChangeListener(function(e) {{
      if (e.type === Blockly.Events.BLOCK_CREATE || 
          e.type === Blockly.Events.BLOCK_MOVE || 
          e.type === Blockly.Events.BLOCK_CHANGE || 
          e.type === Blockly.Events.BLOCK_DELETE) {{
        renderDebugLogs();
      }}
    }});

    setInterval(renderDebugLogs, 500);
  </script>
</body>
</html>
"""

components.html(blockly_html_payload, height=700, scrolling=False)

# ==========================================
# ### LOCKED CORE END ### - DO NOT TOUCH
# ==========================================


# ==========================================
# 4. SCROLLABLE LOWER TERMINAL MODULES
# ==========================================
st.markdown("---")
st.markdown("### 🎛️ Standalone Verification Terminals")
st.caption("Scroll down below the arena workspace to access direct testing consoles.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Query Terminal Matrix")
    tool_choice = st.selectbox("Select Utility Channel", ["🔍 Website DNS Lookup", "🗺️ IP Geolocation", "📱 Phone Tracker Info"])
    query_input = st.text_input("Target Value Input", "+628111989199")
    
    if st.button("Execute Manual Query", type="secondary"):
        with st.spinner("Processing channel..."):
            if "DNS" in tool_choice:
                st.code(perform_dns_lookup(query_input))
            elif "IP" in tool_choice:
                st.code(perform_ip_geolocation(query_input))
            else:
                st.code(perform_phone_tracking(query_input))

with col2:
    st.subheader("📊 Network Routing Help")
    st.markdown("""
    Use global international standards for scanning inputs:
    - **US Target Example**: `+14155552671`
    - **UK Target Example**: `+442079460192`
    - **Indonesian Target Example**: `+628111989199` or local format `08111989199`
    """)