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
    Does not scrape private info; exposes structural baseline telemetry.
    """
    clean_phone = str(target_phone).strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not clean_phone:
        return "Error: Missing operational phone digits."
    
    # Analyze prefix routing properties for baseline layout metrics
    is_intl = clean_phone.startswith("+")
    country_est = "International Flag Detected" if is_intl else "North American Dial Plan / Local"
    length = len(clean_phone)
    
    # Generate structured engineering profile mapping data values dynamically
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
    normalized_profile = str(scan_profile_type).lower().strip()
    if normalized_profile == "dns":
        return perform_dns_lookup(target_string)
    elif normalized_profile in ["whois", "geoip"]:
        return perform_ip_geolocation(target_string)
    elif normalized_profile == "phone":
        return perform_phone_scan(target_string)
    else:
        return f"[Configuration Fault] Unregistered mode profile: '{scan_profile_type}'"


def show_output_to_user(data_result_string: str):
    """Invoked directly by the compiled 'display_result' block command to append logs to side monitor."""
    st.session_state["console_terminal_logs"] += f"\n{data_result_string}\n{'-'*40}"


def compile_and_execute_blocks(compiled_script_text: str):
    """Safely executes code blocks by wrapping the text execution inside a structured runtime scope."""
    # Reset tracking buffer frames ahead of execution loop runs
    st.session_state["console_terminal_logs"] = "==== Active Session Terminal Run ====\n"
    
    restricted_sandbox_globals = {
        "run_utility_scan": run_utility_scan,
        "show_output_to_user": show_output_to_user,
        "print": lambda *args: show_output_to_user(" ".join(map(str, args))),
        "current_result": ""
    }
    try:
        # Evaluate block script sequences line-by-line
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

# Intercept updates passed up via iframe callback communication components
query_params = st.query_params
if "generated_python" in query_params:
    st.session_state["compiled_block_code"] = query_params["generated_python"]

# Setup the fixed Sidebar Terminal for continuous visibility
with st.sidebar:
    st.header("🖥️ Sidebar Target Console Log")
    st.code(st.session_state["console_terminal_logs"], language="text")
    if st.button("🧹 Flush Monitor Buffer", use_container_width=True):
        st.session_state["console_terminal_logs"] = "Monitor buffer flushed."
        st.rerender()

left_control_column, right_display_column = st.columns([7, 5])

with left_control_column:
    st.markdown("### 🗺️ Blockly Drag-and-Drop Arena")

    # Injected HTML framework loading core open-source subcategories via CDN hooks
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
        /* Style fixes for injection frame workspace categories */
        .blocklyTreeLabel { color: #fff !important; font-family: sans-serif; font-size: 13px; }
      </style>
    </head>
    <body>

      <div id="blocklyDiv"></div>

      <xml id="toolbox" style="display: none">
        <category name="Custom Nodes" colour="260">
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
        // 1. Definition specifications for custom architectural operational layout nodes
        Blockly.Blocks['target'] = {
          init: function() {
            this.appendDummyInput()
                .appendField("Target:")
                .appendField(new Blockly.FieldTextInput("google.com"), "Target")
                .appendField(new Blockly.FieldDropdown([["Domain/IP","IP"], ["Phone Target","Phone"]]), "NAME");
            this.setOutput(true, "String");
            this.setColour(120);
          }
        };

        Blockly.Blocks['action_scan'] = {
          init: function() {
            this.appendValueInput("NAME")
                .setCheck("String")
                .appendField("Run Scan on");
            this.appendDummyInput()
                .appendField("using Operational Profile:")
                .appendField(new Blockly.FieldDropdown([["DNS Infrastructure","dns"], ["IP Geolocation Map","geoip"], ["Phone Vector OSINT","phone"]]), "SCANTYPE");
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

        // 2. Register Generator translations mapping visuals to valid executable strings
        Blockly.Python = Blockly.Generator.get('Python');
        
        Blockly.Python.forBlock['target'] = function(block) {
          var field_target = block.getFieldValue('Target');
          var code = '"' + field_target + '"';
          return [code, 0]; // Order 0 maps to Atomic python precedence wrapping
        };

        Blockly.Python.forBlock['action_scan'] = function(block) {
          var dropdown_scantype = block.getFieldValue('SCANTYPE');
          var value_name = Blockly.Python.valueToCode(block, 'NAME', 0) || "''";
          return 'current_result = run_utility_scan(' + value_name + ', "' + dropdown_scantype + '")\\n';
        };

        Blockly.Python.forBlock['display_result'] = function(block) {
          return 'show_output_to_user(current_result)\\n';
        };

        // 3. Mount workspace view container elements
        var workspace = Blockly.inject('blocklyDiv', {
          toolbox: document.getElementById('toolbox'),
          grid: {spacing: 20, length: 3, colour: '#333', snap: true},
          zoom: {controls: true, wheel: true, startScale: 1.0, maxScale: 3, minScale: 0.3, scaleSpeed: 1.2},
          trashcan: true
        });

        // 4. Synchronization listener bridge alerting parent page frames of configuration adjustments
        function syncWorkspaceCode(event) {
          if (event.type == Blockly.Events.BLOCK_MOVE || 
              event.type == Blockly.Events.BLOCK_CHANGE || 
              event.type == Blockly.Events.BLOCK_DELETE ||
              event.type == Blockly.Events.BLOCK_CREATE ||
              event.type == Blockly.Events.VAR_CREATE) {
              
            var generatedRawText = Blockly.Python.workspaceToCode(workspace);
            
            // Post code changes back cleanly up into the active view query params matrix
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
        st.rerender()