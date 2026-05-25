import socket
import json
import urllib.request
import streamlit as st

# Initialize execution state in Streamlit's session state to persist data across clicks
if "workspace_output_data" not in st.session_state:
    st.session_state["workspace_output_data"] = "No actions executed yet."

# ==========================================
# 1. CORE UTILITY SCAN FUNCTIONS (The Backend)
# ==========================================

def perform_dns_lookup(target: str) -> str:
    """Performs a standard forward DNS lookup to resolve a hostname to an IP address."""
    clean_target = target.strip().replace(" ", "")
    if not clean_target:
        return "Error: Target is empty."
    
    try:
        ip_address = socket.gethostbyname(clean_target)
        return f"[DNS Lookup Success]\nHostname: {clean_target}\nResolved IP: {ip_address}"
    except socket.gaierror:
        return f"[DNS Lookup Error]\nCould not resolve hostname: '{clean_target}'"
    except Exception as e:
        return f"[Error] Unexpected issue during DNS resolution: {str(e)}"


def perform_ip_geolocation(target: str) -> str:
    """
    Looks up basic geographic routing info for an IP or host.
    Uses a standard open-access public API securely.
    """
    clean_target = target.strip().replace(" ", "")
    if not clean_target:
        return "Error: Target is empty."
        
    try:
        # Resolve hostname to IP first if a domain name was provided
        try:
            resolved_ip = socket.gethostbyname(clean_target)
        except socket.gaierror:
            return f"[IP Lookup Error]\nCould not resolve target '{clean_target}' to a valid IP layout."

        # Fetch basic geo JSON record
        url = f"http://ip-api.com/json/{resolved_ip}"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            
        if data.get("status") == "fail":
            return f"[IP Lookup Failed]\nMessage: {data.get('message', 'Unknown error')}"
            
        output_lines = [
            "[IP Geolocation Data]",
            f"Target Host: {clean_target}",
            f"Query IP:    {data.get('query')}",
            f"Country:     {data.get('country')} ({data.get('countryCode')})",
            f"Region/City: {data.get('regionName')}, {data.get('city')}",
            f"ISP:         {data.get('isp')}",
            f"ASN:         {data.get('as')}"
        ]
        return "\n".join(output_lines)
        
    except Exception as e:
        return f"[Error] Infrastructure query failed: {str(e)}"


# ==========================================
# 2. THE COMPILER RUNTIME INTERFACE (The Glue)
# ==========================================

def run_utility_scan(target: str, scan_type: str) -> str:
    """
    Central dispatcher called directly by your generated blockly code strings.
    """
    if scan_type == "dns":
        st.session_state["workspace_output_data"] = perform_dns_lookup(target)
    elif scan_type == "whois":
        # Hooking up IP routing/Geo metrics to the Whois selector slot
        st.session_state["workspace_output_data"] = perform_ip_geolocation(target)
    else:
        st.session_state["workspace_output_data"] = f"Unknown operational block mode selected: {scan_type}"
        
    return st.session_state["workspace_output_data"]


def show_output_to_user(data_content: str):
    """
    Invoked by the brown statement log block to write values to the active Streamlit app view.
    """
    # Simply guarantees the state is captured; rendering is handled natively below
    pass


def execute_workspace_blocks(generated_python_code: str):
    """
    Safely interprets the blockly workspace pipeline using an isolated local execution state environment.
    """
    # Strict dictionary execution scope containing ONLY the pre-approved backend actions
    execution_scope = {
        "run_utility_scan": run_utility_scan,
        "show_output_to_user": show_output_to_user,
        "current_result": st.session_state["workspace_output_data"]
    }
    
    try:
        # Executes the generated script string sequentially line by line
        exec(generated_python_code, execution_scope)
    except Exception as exec_error:
        st.error(f"Workspace Runtime Exception: {str(exec_error)}")


# ==========================================
# 3. STREAMLIT APP LAYOUT & CONTROL FRONTEND
# ==========================================

st.set_page_config(page_title="EZHack Dashboard", layout="wide")

st.title("🛡️ EZHack Toolkit — Visual Studio")
st.caption("Modular automation framework driven by user-defined visual block layouts.")

# Creating two clean workspace column segments
col_canvas, col_results = st.columns([3, 2])

with col_canvas:
    st.subheader("Workspace Pipeline Configuration")
    
    # ⚠️ PLACEHOLDER/MOCK FOR CODING SIMULATION: 
    # In your full implementation, this text variable string should receive the text directly from 
    # the frontend javascript injection code snippet when compiling the workspace blocks!
    mock_generated_code = (
        'current_result = run_utility_scan("example.com", "dns")\n'
        'show_output_to_user(current_result)\n'
    )
    
    st.info("💡 **Block Code Translation View** (Simulated compile output shown below)")
    workspace_code_text = st.text_area(
        label="Active Blockly Python Code Generation Output String:",
        value=mock_generated_code,
        height=150
    )
    
    trigger_execution = st.button("▶ Run Workspace Actions", type="primary")

with col_results:
    st.subheader("Console Output Log")
    
    if trigger_execution:
        with st.spinner("Processing workspace pipeline..."):
            execute_workspace_blocks(workspace_code_text)
            
    # Output presentation container box
    st.markdown("### Execution Terminal Window:")
    st.code(st.session_state["workspace_output_data"], language="text")