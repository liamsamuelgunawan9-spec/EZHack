import os
import socket
import json
import urllib.request
import streamlit as st

# Verify initialization of tracking logs in the local session engine
if "console_terminal_logs" not in st.session_state:
    st.session_state["console_terminal_logs"] = "System Context: Awaiting block layout execution instructions..."

# ==========================================
# 1. CORE UTILITY EXTRACTION LOGIC
# ==========================================

def perform_dns_lookup(target: str) -> str:
    """Performs standard forward infrastructure DNS lookups."""
    clean_host = target.strip().replace(" ", "")
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
    clean_host = target.strip().replace(" ", "")
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
            return f"[GeoIP Target Failure]\nResponse Code: {json_payload.get('message', 'Unknown endpoint parsing error')}"
            
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


# ==========================================
# 2. RUNTIME SANDBOX TRANSLATOR PIPELINE
# ==========================================

def run_utility_scan(target_string: str, scan_profile_type: str) -> str:
    """Central dispatcher function dynamically executed by the blockly string mapping sequence."""
    normalized_profile = scan_profile_type.lower().strip()
    
    if normalized_profile == "dns":
        execution_output = perform_dns_lookup(target_string)
    elif normalized_profile in ["whois", "nmap", "geoip"]:
        execution_output = perform_ip_geolocation(target_string)
    else:
        execution_output = f"[Configuration Fault] Unregistered execution mode profile: '{scan_profile_type}'"
        
    return execution_output


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

# Debugging tool sidebar: Displays and verifies the JavaScript assets we loaded
with st.sidebar:
    st.header("📦 Registered JS Assets")
    assets_dir = "assets"
    if os.path.exists(assets_dir):
        js_files = [f for f in os.listdir(assets_dir) if f.endswith(".js")]
        for js_file in js_files:
            st.success(f"Loaded block file: `{js_file}`")
    else:
        st.error("Missing standard directory location: `assets/` folder not found.")

left_control_column, right_display_column = st.columns([1, 1])

with left_control_column:
    st.markdown("### 📝 Code Generation Buffer View")
    st.caption("This matches the raw layout code string passed when chaining your custom blocks together.")
    
    # Pre-loading mock text data layout showing exactly how your three updated blocks chain together seamlessly:
    sample_block_code_output = (
        'current_result = run_utility_scan("google.com", "dns")\n'
        'show_output_to_user(current_result)\n'
    )
    
    raw_text_input_stream = st.text_area(
        label="Blockly Code Output Window:",
        value=sample_block_code_output,
        height=180,
        label_visibility="collapsed"
    )
    
    trigger_pipeline_run = st.button("🚀 Fire Workspace Pipeline Execution", type="primary", use_container_width=True)

with right_display_column:
    st.markdown("### 🖥️ Realtime Output Monitor Terminal")
    
    if trigger_pipeline_run:
        with st.spinner("Compiling script state sequences..."):
            compile_and_execute_blocks(raw_text_input_stream)
            
    st.code(st.session_state["console_terminal_logs"], language="text")