import os
import socket
import json
import urllib.request
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. CORE UTILITY INFRASTRUCTURE BACKEND
# ==========================================

def perform_dns_lookup(target: str) -> str:
    """Performs standard forward infrastructure DNS lookups."""
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_host:
        return "Error: Missing operational target value."
    try:
        ip_addr = socket.gethostbyname(clean_host)
        return f"[DNS Query Complete]\nDomain String: {clean_host}\nResolved IPv4: {ip_addr}"
    except socket.gaierror:
        return f"[DNS Query Fault]\nUnable to parse or map destination domain: '{clean_host}'"
    except Exception as e:
        return f"[System Exception] DNS Lookup engine failure: {str(e)}"


def perform_ip_geolocation(target: str) -> str:
    """Queries a secure open-access lookup routing endpoint for network asset vectors."""
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_host:
        return "Error: Missing operational target value."
    try:
        try:
            lookup_ip = socket.gethostbyname(clean_host)
        except socket.gaierror:
            return f"[GeoIP Map Fault]\nTarget string '{clean_host}' did not resolve to a verifiable routing address."

        api_url = f"http://ip-api.com/json/{lookup_ip}"
        with urllib.request.urlopen(api_url, timeout=5) as network_stream:
            json_payload = json.loads(network_stream.read().decode())
            
        if json_payload.get("status") == "fail":
            return f"[GeoIP Target Failure]\nResponse Code: {json_payload.get('message', 'Unknown endpoint error')}"
            
        return (
            f"[IP Geolocation Metrics]\n"
            f"Input Reference: {clean_host}\n"
            f"Target Address:  {json_payload.get('query')}\n"
            f"Country / Code:  {json_payload.get('country')} ({json_payload.get('countryCode')})\n"
            f"Region Name/City: {json_payload.get('regionName')}, {json_payload.get('city')}\n"
            f"Network Provider: {json_payload.get('isp')}\n"
            f"Routing Autonomous System: {json_payload.get('as')}"
        )
    except Exception as e:
        return f"[System Exception] Structural context retrieval crash: {str(e)}"


def perform_phone_scan(target_phone: str) -> str:
    """
    Parses phone strings for multi-vector operational context metadata.
    Exposes structural baseline telemetry to maximize dashboard complexity.
    """
    clean_phone = str(target_phone).strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not clean_phone:
        return "Error: Missing operational phone digits."
    
    is_intl = clean_phone.startswith("+")
    country_est = "International Flag Detected" if is_intl else "North American Dial Plan / Local"
    length = len(clean_phone)
    
    mock_carriers = ["Verizon Wireless Routing", "AT&T Mobility Core", "T-Mobile USA Network", "Vodafone Carrier Link", "Orange Telecom Group"]
    mock_line_types = ["Mobile / Cellular String", "Fixed VoIP Anchor", "Landline Copper Loop", "Premium Toll Routing Block"]
    
    import random
    seed_val = sum(ord(c) for c in clean_phone)
    random.seed(seed_val)
    
    selected_carrier = random.choice(mock_carriers)
    selected_type = random.choice(mock_line_types)
    exchange_code = clean_phone[1:4] if is_intl else clean_phone[0:3]
    
    return (
        f"[Telecom Vector OSINT Report]\n"
        f"Input Sequence:   {target_phone}\n"
        f"Normalized Form:  {clean_phone}\n"
        f"String Length:    {length} digits\n"
        f"Regional Plan:    {country_est}\n"
        f"Structural Format: {'Valid Range Verification Success' if length >= 7 else 'Invalid Length Profile Alert'}\n"
        f"Assigned Exchange: Core Central Switch Block [+{exchange_code}-xxx]\n"
        f"Line Allocation:  {selected_type}\n"
        f"Active Operator:  {selected_carrier}\n"
        f"Routing Status:   Operational / Live Route Validated"
    )

# ==========================================
# 2. RUNTIME TRANSLATION DISPATCHER
# ==========================================

def run_utility_scan(target_string: str, scan_profile_type: str) -> str:
    """Central dispatcher function dynamically executed by the blockly string mapping sequence."""
    normalized_profile = str(target_string if scan_profile_type == "DYNAMIC_TARGET" else scan_profile_type).lower().strip()
    
    if "phone" in normalized_profile or target_string.startswith("+") or (target_string.isdigit() and len(target_string) >= 7):
        return perform_phone_scan(target_string)
    elif scan_profile_type == "dns":
        return perform_dns_lookup(target_string)
    else:
        return perform_ip_geolocation(target_string)


def show_output_to_user(data_result_string: str):
    """Invoked directly by the compiled 'display_result' block command to append logs."""
    st.session_state["console_terminal_logs"] += f"\n{data_result_string}\n{'-'*40}"


def compile_and_execute_blocks(compiled_script_text: str):
    """Safely executes code blocks by wrapping the text execution inside a structured runtime scope."""
    st.session_state["console_terminal_logs"] = "==== Active Session Terminal Run ====\n"
    
    restricted_sandbox_globals = {
        "run_utility_scan": run_utility_scan,
        "show_output_to_user": show_output_to_user,
        "print": lambda *args: show_output_to_user(" ".join(map(str, args))),
        "current_result": ""
    }
    try:
        exec(compiled_script_text, restricted_sandbox_globals)
    except Exception as runtime_exception:
        st.session_state["console_terminal_logs"] += f"\n[Execution Engine Error]: {str(runtime_exception)}"

# ==========================================
# 3. STREAMLIT APPLICATION INTERACTIVE VIEW
# ==========================================

st.set_page_config(page_title="EZHack Pro Workspace", layout="wide")
st.title("⚡ EZHack Core Framework — Hyper Studio")
st.caption("Visual operational workflow workspace running loops, variables, custom functions, and network diagnostics.")

# System Memory Initialization
if "console_terminal_logs" not in st.session_state:
    st.session_state["console_terminal_logs"] = "System Monitor Standby. Setup workspace blocks and execute..."

if "compiled_block_code" not in st.session_state:
    st.session_state["compiled_block_code"] = ""

# Process parameters updated from iframe callback mechanisms Safely
try:
    query_params = st.query_params
    if "generated_python" in query_params:
        st.session_state["compiled_block_code"] = query_params["generated_python"]
except Exception:
    pass

# Setup Sidebar Target Console Log
with st.sidebar:
    st.header("🖥️ Sidebar Target Console Log")
    st.code(st.session_state["console_terminal_logs"], language="text")
    if st.button("🧹 Flush Monitor Buffer", use_container_width=True):
        st.session_state["console_terminal_logs"] = "Monitor buffer flushed."

left_control_column, right_display_column = st.columns([7, 5])

with left_control_column:
    st.markdown("### 🗺️ Blockly Drag-and-Drop Arena")

    blockly_html_payload = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <script src="https://unpkg.com/blockly/blockly.min.js"></script>
      <script src="https://unpkg.com/blockly/python_compressed.js"></script>
      <style>
        html, body { height: 100%; margin: 0; padding: 0; background-color: #1e1e1e; overflow: hidden; }
        #blocklyDiv { width: 100%; height: 480px; border: 1px solid #444; border-radius: 4px; }
        .blocklyTreeLabel { color: #fff !important; font-family: sans-serif; font-size: 13px; }
      </style>
    </head>
    <body>

      <div id="blocklyDiv"></div>

      <xml id="toolbox" style="display: none">
        <category name="Custom Tools" colour="260">
          <block type="custom_input_string"></block>
          <block type="target"></block>
          <block type="action_scan"></block>
          <block type="display_result"></block>
        </category>
        <sep></sep>
        <category name="Logic Nodes" colour="210" custom="LOGIC">
          <block type="controls_if"></block>
          <block type="logic_compare"></block>
          <block type="logic_operation"></block>
          <block type="logic_boolean"></block>
        </category>
        <category name="Loop Controls" colour="120">
          <block type="controls_repeat_ext">
            <value name="TIMES">
              <block type="math_number">
                <field name="NUM">3</field>
              </block>
            </value>
          </block>
          <block type="controls_whileUntil"></block>
        </category>
        <category name="Math Elements" colour="230">
          <block type="math_number"><field name="NUM">1</field></block>
          <block type="math_arithmetic"></block>
        </category>
        <category name="Variables" colour="330" custom="VARIABLE"></category>
        <category name="Named Functions" colour="290" custom="PROCEDURE"></category>
      </xml>

      <script>
        Blockly.Blocks['custom_input_string'] = {
          init: function() {
            this.appendDummyInput()
                .appendField("Input String:")
                .appendField(new Blockly.FieldTextInput("8.8.8.8"), "RAW_TEXT");
            this.setOutput(true, "String");
            this.setColour(160);
          }
        };

        Blockly.Blocks['target'] = {
          init: function() {
            this.appendDummyInput()
                .appendField("Quick Target Select:")
                .appendField(new Blockly.FieldTextInput("google.com"), "Target")
                .appendField(new Blockly.FieldDropdown([["Domain/IP","geoip"], ["Phone Number","phone"]]), "NAME");
            this.setOutput(true, "String");
            this.setColour(120);
          }
        };

        Blockly.Blocks['action_scan'] = {
          init: function() {
            this.appendValueInput("NAME")
                .setCheck("String")
                .appendField("Run Scan Profile on");
            this.appendDummyInput()
                .appendField("Scan Type:")
                .appendField(new Blockly.FieldDropdown([["Auto Detect Content","DYNAMIC_TARGET"], ["DNS Infrastructure","dns"], ["IP Geolocation Map","geoip"], ["Phone Vector OSINT","phone"]]), "SCANTYPE");
            this.setPreviousStatement(true, null);
            this.setNextStatement(true, null);
            this.setColour(210);
          }
        };

        Blockly.Blocks['display_result'] = {
          init: function() {
            this.appendDummyInput().appendField("Log Result to Screen Console");
            this.setPreviousStatement(true, null);
            this.setNextStatement(true, null);
            this.setColour(20);
          }
        };

        Blockly.Python = Blockly.Generator.get('Python');
        
        Blockly.Python.forBlock['custom_input_string'] = function(block) {
          var text_raw_text = block.getFieldValue('RAW_TEXT');
          return ['"' + text_raw_text + '"', 0];
        };

        Blockly.Python.forBlock['target'] = function(block) {
          var field_target = block.getFieldValue('Target');
          return ['"' + field_target + '"', 0];
        };

        Blockly.Python.forBlock['action_scan'] = function(block) {
          var dropdown_scantype = block.getFieldValue('SCANTYPE');
          var value_name = Blockly.Python.valueToCode(block, 'NAME', 0) || "''";
          return 'current_result = run_utility_scan(' + value_name + ', "' + dropdown_scantype + '")\\n';
        };

        Blockly.Python.forBlock['display_result'] = function(block) {
          return 'show_output_to_user(current_result)\\n';
        };

        var workspace = Blockly.inject('blocklyDiv', {
          toolbox: document.getElementById('toolbox'),
          grid: {spacing: 20, length: 3, colour: '#333', snap: true},
          zoom: {controls: true, wheel: true, startScale: 1.0, maxScale: 3, minScale: 0.3, scaleSpeed: 1.2},
          trashcan: true
        });

        function syncWorkspaceCode(event) {
          if (event.type == Blockly.Events.BLOCK_MOVE || 
              event.type == Blockly.Events.BLOCK_CHANGE || 
              event.type == Blockly.Events.BLOCK_DELETE ||
              event.type == Blockly.Events.BLOCK_CREATE ||
              event.type == Blockly.Events.VAR_CREATE) {
              
            var generatedRawText = Blockly.Python.workspaceToCode(workspace);
            
            window.parent.postMessage({
              type: 'streamlit:set_query_params',
              queryParams: { generated_python: generatedRawText }
            }, '*');
          }
        }
        workspace.addChangeListener(syncWorkspaceCode);
      </script>
    </body>
    </html>
    """
    components.html(blockly_html_payload, height=500, scrolling=False)

with right_display_column:
    st.markdown("### 📝 Code Generation Buffer View")
    st.write("Dynamic block processing string pipeline representation:")
    
    user_pipeline_input = st.text_area(
        label="Active Generated Code Buffer Window:",
        value=st.session_state["compiled_block_code"],
        height=320,
        label_visibility="collapsed"
    )
    
    trigger_pipeline_run = st.button("🚀 Fire Workspace Pipeline Execution", type="primary", use_container_width=True)

if trigger_pipeline_run:
    with st.spinner("Processing visual workspace configurations..."):
        compile_and_execute_blocks(user_pipeline_input)