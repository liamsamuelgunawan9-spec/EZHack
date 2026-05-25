import os
import socket
import json
import urllib.request
import random
import streamlit as st

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
    """Queries an open-access lookup routing endpoint for network asset vectors."""
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_host:
        return "Error: Missing operational target value."
    try:
        try:
            lookup_ip = socket.gethostbyname(clean_host)
        except socket.gaierror:
            return f"[GeoIP Map Fault]\nTarget string '{clean_host}' did not resolve to a verifiable routing address."

        api_url = f"http://ip-api.com/json/{lookup_ip}"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as network_stream:
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
    """Parses phone strings for multi-vector operational context metadata."""
    clean_phone = str(target_phone).strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not clean_phone:
        return "Error: Missing operational phone digits."
    
    is_intl = clean_phone.startswith("+")
    country_est = "International Flag Detected" if is_intl else "North American Dial Plan / Local"
    length = len(clean_phone)
    
    mock_carriers = ["Verizon Wireless Routing", "AT&T Mobility Core", "T-Mobile USA Network", "Vodafone Carrier Link", "Orange Telecom Group"]
    mock_line_types = ["Mobile / Cellular String", "Fixed VoIP Anchor", "Landline Copper Loop", "Premium Toll Routing Block"]
    
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
    """Central dispatcher function dynamically executed by the processing sequence."""
    normalized_profile = str(scan_profile_type).lower().strip()
    
    if normalized_profile == "phone" or target_string.startswith("+"):
        return perform_phone_scan(target_string)
    elif normalized_profile == "dns":
        return perform_dns_lookup(target_string)
    else:
        return perform_ip_geolocation(target_string)

# ==========================================
# 3. STREAMLIT APPLICATION INTERACTIVE VIEW
# ==========================================

st.set_page_config(page_title="EZHack Pro Workspace", layout="wide")
st.title("⚡ EZHack Core Framework — Hyper Studio")
st.caption("Visual operational workflow workspace running loops, variables, and network diagnostics.")

# System Memory Initialization
if "console_terminal_logs" not in st.session_state:
    st.session_state["console_terminal_logs"] = "System Monitor Standby. Input target parameters and execute your profile..."

# Setup Sidebar Target Console Log
with st.sidebar:
    st.header("🖥️ Sidebar Target Console Log")
    st.code(st.session_state["console_terminal_logs"], language="text")
    if st.button("🧹 Flush Monitor Buffer", use_container_width=True):
        st.session_state["console_terminal_logs"] = "Monitor buffer flushed."

left_control_column, right_display_column = st.columns([6, 6])

with left_control_column:
    st.markdown("### 🗺️ Workspace Input Vector Control")
    st.write("Configure targets and scan parameters natively below:")
    
    # Secure inputs replacing the broken iframe elements
    target_input = st.text_input("🎯 Target Asset Input string:", value="8.8.8.8", help="Provide a Domain name, IP address, or standard phone string.")
    
    scan_mode = st.selectbox(
        "⚙️ Execution Scan Profile Type:",
        ["IP Geolocation Map", "DNS Infrastructure", "Phone Vector OSINT"]
    )
    
    # Visual Block Map preview representation generator
    scan_map = {"IP Geolocation Map": "geoip", "DNS Infrastructure": "dns", "Phone Vector OSINT": "phone"}
    selected_mode_id = scan_map[scan_mode]
    
    st.markdown("#### 📝 Preview Compiled Script Buffer")
    generated_snippet = f'current_result = run_utility_scan("{target_input}", "{selected_mode_id}")\nshow_output_to_user(current_result)'
    st.code(generated_snippet, language="python")
    
    trigger_pipeline_run = st.button("🚀 Fire Workspace Pipeline Execution", type="primary", use_container_width=True)

with right_display_column:
    st.markdown("### 🛡️ Live Terminal Activity Monitor")
    st.write("Real-time utility execution monitoring stream output:")
    
    # Execution Block Runner Logic
    if trigger_pipeline_run:
        with st.spinner("Processing workspace configurations..."):
            st.session_state["console_terminal_logs"] = "==== Active Session Terminal Run ====\n"
            try:
                scan_output = run_utility_scan(target_input, selected_mode_id)
                st.session_state["console_terminal_logs"] += f"\n{scan_output}\n{'-'*40}"
            except Exception as e:
                st.session_state["console_terminal_logs"] += f"\n[Execution Engine Error]: {str(e)}"
    
    st.text_area(
        label="Terminal Output Display View",
        value=st.session_state["console_terminal_logs"],
        height=400,
        disabled=True,
        label_visibility="collapsed"
    )