import os
import socket
import json
import urllib.request
import streamlit as st
import streamlit.components.v1 as components

# 1. Initialize global system states
if "console_terminal_logs" not in st.session_state:
    st.session_state["console_terminal_logs"] = "System Context: Awaiting block layout execution instructions..."

# ==========================================
# 2. CORE UTILITY EXTRACTION LOGIC
# ==========================================

def perform_dns_lookup(target: str) -> str:
    """Performs standard forward infrastructure DNS lookups."""
    clean_host = target.strip().replace(" ", "").replace('"', '').replace("'", "")
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
    clean_host = target.strip().replace(" ", "").replace('"', '').replace("'", "")
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
            return f"[GeoIP Target Failure]\nResponse Code: {json_payload.get('message', 'Unknown error')}"
            
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


def run_utility_scan(target_string: str, scan_profile_type: str) -> str:
    """Central dispatcher function dynamically executed by the blockly string mapping sequence."""
    normalized_profile = scan_profile_type.lower().strip()
    if normalized_profile == "dns":
        return perform_dns_lookup(target_string)
    elif normalized_profile in ["whois", "nmap", "geoip"]:
        return perform_ip_geolocation(target_string)
    else:
        return f"[Configuration Fault] Unregistered mode profile: '{scan_profile_type}'"


def show_output_to_user(data_result_string: str):
    """Invoked directly by the compiled 'display_result' block command to lock results into state."""
    st.session_state["console_terminal_logs"] = data_result_string


def compile_and_execute_blocks(compiled_script_text: str):
    """Safely executes code blocks by wrapping the text execution inside a structured runtime scope."""
    restricted_sandbox_globals = {
        "run_utility_scan": run_utility_scan,
        "show_output_to_user": show_output_to_user,
        "current_result": ""
    }
    try:
        exec(compiled_script_text, restricted_sandbox_globals)
    except Exception as runtime_exception:
        st.error(f"Execution Error inside Workspace: {str(runtime_exception)}")


# ==========================================
# 3. STREAMLIT FRAMEWORK LAYOUT & LOADER
# ==========================================

st.set_page_config(page_title="EZHack Dashboard", layout="wide")
st.title("🛡️ EZHack Toolkit — Scripting Control Workspace")

# Debugging tool sidebar verifying raw file imports
with st.sidebar:
    st.header("📦 Registered JS Assets")
    assets_dir = "assets"
    if os.path.exists(assets_dir):
        js_files = [f for f in os.listdir(assets_dir) if f.endswith(".js")]
        for js_file in js_files:
            st.success(f"Loaded script: `{js_file}`")
    else:
        st.error("Missing folder directory locate: `assets/` not found.")

left_control_column, right_display_column = st.columns([3, 2])

with left_control_column:
    st.markdown("### 🗺️ Blockly Drag-and-Drop Arena")
    
    # Complete raw HTML canvas injection payload containing script dependencies
    blockly_html_payload = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <script src="https://unpkg.com/blockly/blockly.min.js"></script>
      <style>
        html, body { height: 100%; margin: 0; padding: 0; background-color: #1e1e1e; color: #ffffff; font-family: sans-serif; }
        #blocklyDiv { width: 100%; height: 400px; border: 1px solid #444; border-radius: 4px; }
      </style>
    </head>
    <body>

      <div id="blocklyDiv"></div>

      <xml id="toolbox" style="display: none">
        <category name="Inputs" colour="120">
          <block type="target"></block>
        </category>
        <category name="Actions" colour="210">
          <block type="action_scan"></block>
        </category>
        <category name="Reporters" colour="20">
          <block type="display_result"></block>
        </category>
      </xml>

      <script>
        // 1. Structural target configurations matching your custom block fields
        Blockly.Blocks['target'] = {
          init: function() {
            this.appendDummyInput()
                .appendField("Target:")
                .appendField(new Blockly.FieldTextInput("google.com"), "Target")
                .appendField(new Blockly.FieldDropdown([["IP","IP"], ["Domain","Domain"]]), "NAME");
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
                .appendField("using")
                .appendField(new Blockly.FieldDropdown([["DNS Lookup","DNS"], ["IP Geolocation","WHOIS"]]), "SCANTYPE");
            this.setPreviousStatement(true, null);
            this.setNextStatement(true, null);
            this.setColour(210);
          }
        };

        Blockly.Blocks['display_result'] = {
          init: function() {
            this.appendDummyInput().appendField("Log Result to Screen");
            this.setPreviousStatement(true, null);
            this.setNextStatement(true, null);
            this.setColour(20);
          }
        };

        // 2. Inject the engine layout into browser container space
        var workspace = Blockly.inject('blocklyDiv', {
          toolbox: document.getElementById('toolbox'),
          grid: {spacing: 20, length: 3, colour: '#333', snap: true},
          trashcan: true
        });
      </script>
    </body>
    </html>
    """
    
    # Rendering the HTML framework directly inside the Streamlit column layout
    components.html(blockly_html_payload, height=420, scrolling=False)
    
    st.markdown("### 📝 Code Generation Buffer View")
    sample_block_code_output = (
        'current_result = run_utility_scan("google.com", "dns")\n'
        'show_output_to_user(current_result)\n'
    )
    
    raw_text_input_stream = st.text_area(
        label="Active Execution Stream Buffer Window:",
        value=sample_block_code_output,
        height=100,
        label_visibility="collapsed"
    )
    
    trigger_pipeline_run = st.button("🚀 Fire Workspace Pipeline Execution", type="primary", use_container_width=True)

with right_display_column:
    st.markdown("### 🖥️ Realtime Output Monitor Terminal")
    
    if trigger_pipeline_run:
        with st.spinner("Compiling script state sequences..."):
            compile_and_execute_blocks(raw_text_input_stream)
            
    st.code(st.session_state["console_terminal_logs"], language="text")