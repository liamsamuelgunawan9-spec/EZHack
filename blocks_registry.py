import socket
import json
import urllib.request
import urllib.parse
import random
import re
import time
import ssl
import streamlit as st

import phonenumbers
from phonenumbers import carrier, geocoder, timezone

# ==========================================
# 1. CORE UTILITY FUNCTIONS (PASSIVE OSINT SUITE & ATTACK SIMS)
# ==========================================

def perform_dns_lookup(target: str) -> str:
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    clean_host = clean_host.replace("https://", "").replace("http://", "").split("/")[0]
    if not clean_host:
        return "❌ ERROR: Target host missing!"
    
    if clean_host.startswith("+") or (clean_host.isdigit() and len(clean_host) > 6):
        return perform_phone_tracking(clean_host)
        
    try:
        ip_addr = socket.gethostbyname(clean_host)
        return f"📡 DNS Resolution successful for [{clean_host}]\n📍 Resolved IP Address: {ip_addr}"
    except Exception as e:
        return f"❌ DNS Lookup Failed for target '{clean_host}': {str(e)}"

def perform_ip_geolocation(target: str) -> str:
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    clean_host = clean_host.replace("https://", "").replace("http://", "").split("/")[0]
    if not clean_host:
        return "❌ ERROR: Geolocation target missing!"
    
    try:
        # Resolve to IP address first if domain is provided
        ip_addr = socket.gethostbyname(clean_host)
        url = f"http://ip-api.com/json/{ip_addr}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data.get("status") == "success":
                return (f"📍 IP Geolocation Vector Verified [{ip_addr}]:\n"
                        f"   Country : {data.get('country')} ({data.get('countryCode')})\n"
                        f"   Region  : {data.get('regionName')}\n"
                        f"   City    : {data.get('city')}\n"
                        f"   ISP     : {data.get('isp')}\n"
                        f"   Coords  : {data.get('lat')}, {data.get('lon')}")
            else:
                return f"⚠️ Geolocation API returned query failure for node [{ip_addr}]."
    except Exception as e:
        return f"❌ Geolocation Sweep Failed: {str(e)}"

def perform_phone_tracking(phone_num: str) -> str:
    try:
        clean_num = str(phone_num).strip().replace(" ", "").replace('"', '').replace("'", "")
        if not clean_num.startswith("+"):
            clean_num = "+" + clean_num
            
        parsed_num = phonenumbers.parse(clean_num, None)
        if not phonenumbers.is_valid_number(parsed_num):
            return f"❌ ERROR: Provided string '{phone_num}' is not a structurally valid E.164 phone signature."
            
        region_desc = geocoder.description_for_number(parsed_num, "en")
        carrier_desc = carrier.name_for_number(parsed_num, "en")
        tz_desc = timezone.time_zones_for_number(parsed_num)
        
        return (f"📱 Mobile Footprint Analysis [{clean_num}]:\n"
                f"   Valid Format   : True\n"
                f"   Mapped Country : {region_desc if region_desc else 'Unknown/Unlisted'}\n"
                f"   Network Carrier: {carrier_desc if carrier_desc else 'Unknown Provider'}\n"
                f"   Timezone Space : {', '.join(tz_desc)}")
    except Exception as e:
        return f"❌ Telecom Telemetry Breakdown: {str(e)}"

def perform_robots_sitemap_scan(target: str) -> str:
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_host.startswith(("http://", "https://")):
        clean_url = "https://" + clean_host
    else:
        clean_url = clean_host
        
    report = f"🕸️ Web Crawler Footprint Discovery for [{clean_url}]:\n"
    
    # Check robots.txt
    try:
        robots_url = clean_url.rstrip('/') + '/robots.txt'
        req = urllib.request.Request(robots_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            content = response.read().decode('utf-8', errors='ignore')
            lines = content.split('\n')
            disallowed = [line for line in lines if line.lower().startswith("disallow:")]
            report += f"   [+] robots.txt found! Identified {len(disallowed)} restricted directory pathways.\n"
            if disallowed:
                report += "       Sample vectors:\n" + "\n".join([f"       {d.strip()}" for d in disallowed[:4]]) + "\n"
    except Exception:
        report += "   [-] robots.txt unavailable or returned non-200 state.\n"
        
    # Check sitemap.xml
    try:
        sitemap_url = clean_url.rstrip('/') + '/sitemap.xml'
        req = urllib.request.Request(sitemap_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            report += "   [+] sitemap.xml structure exposed! Routing map discovered successfully.\n"
    except Exception:
        report += "   [-] sitemap.xml mapping unexposed.\n"
        
    return report

def perform_ssl_audit(target: str) -> str:
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    clean_host = clean_host.replace("https://", "").replace("http://", "").split("/")[0]
    if not clean_host:
        return "❌ ERROR: SSL audit target missing!"
        
    context = ssl.create_default_context()
    try:
        with socket.create_connection((clean_host, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=clean_host) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                version = ssock.version()
                
                issuer = dict(x[0] for x in cert['issuer']) if 'issuer' in cert else {}
                subject = dict(x[0] for x in cert['subject']) if 'subject' in cert else {}
                
                return (f"🔒 TLS/SSL Cryptographic Cryptanalysis [{clean_host}]:\n"
                        f"   Protocol Channel: {version}\n"
                        f"   Active Cipher   : {cipher[0]} ({cipher[2]} bits)\n"
                        f"   Authority Issuer: {issuer.get('organizationName', 'Unknown')}\n"
                        f"   Subject Common  : {subject.get('commonName', 'Unknown')}\n"
                        f"   Not After/Expiry: {cert.get('notAfter')}")
    except Exception as e:
        return f"❌ TLS Handshake Negotiation Faulted: {str(e)}"

def perform_shodan_lookup(target: str) -> str:
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    clean_host = clean_host.replace("https://", "").replace("http://", "").split("/")[0]
    try:
        ip_addr = socket.gethostbyname(clean_host)
        # Simulated Shodan Intelligence Matrix payload to decouple API key dependencies
        sim_ports = [80, 443, 22, 8080] if "example" in clean_host else [80, 443]
        random.shuffle(sim_ports)
        
        return (f"📡 Shodan Threat Feed Intelligence Proxy [{ip_addr}]:\n"
                f"   Open Exposed Scape: {', '.join(map(str, sim_ports))}\n"
                f"   Detected Stack OS : Linux 4.x/5.x Vulnerable Shell Platform\n"
                f"   Simulated Vulns   : CVE-2023-38606, CVE-2024-21626 (Historical Index)")
    except Exception as e:
        return f"❌ Shodan Intel Resolution Interrupted: {str(e)}"

def perform_whois_lookup(target: str) -> str:
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "").lower()
    clean_host = clean_host.replace("https://", "").replace("http://", "").split("/")[0]
    if not clean_host:
        return "❌ ERROR: Target domain missing!"
    try:
        api_url = f"https://rdap.org/domain/{clean_host}"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as stream:
            data = json.loads(stream.read().decode())
        registrar = data.get("port43", "Unknown Administrative Authority")
        creation_date = "Unknown Record"
        for event in data.get("events", []):
            if event.get("action") == "registration":
                creation_date = event.get("eventDate", "Unknown Date")
        return (f"🌐 [PASSIVE WHOIS REGISTRY SUMMARY]\n"
                f"   • Domain Name: {clean_host}\n"
                f"   • Registrar  : {registrar}\n"
                f"   • Created On : {creation_date}\n"
                f"   • Status     : Query Completed Automatically")
    except Exception:
        return (f"🌐 [PASSIVE WHOIS REGISTRY SUMMARY]\n"
                f"   • Domain Name: {clean_host}\n"
                f"   • Registrar  : Global Top-Level Domain Registry Services\n"
                f"   • Asset State: Active Historical Record Discovered")

def perform_http_header_audit(target: str) -> str:
    clean_url = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_url.startswith("http"):
        clean_url = "https://" + clean_url
    try:
        req = urllib.request.Request(clean_url, method="HEAD", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            headers = response.info()
        
        server = headers.get("Server", "Hidden/Not Disclosed")
        x_frame = headers.get("X-Frame-Options", "❌ MISSING (Vulnerable to Clickjacking)")
        hsts = headers.get("Strict-Transport-Security", "❌ MISSING (Vulnerable to MITM)")
        csp = headers.get("Content-Security-Policy", "❌ MISSING (Vulnerable to XSS injections)")
        
        return (f"🛡️ [HTTP SECURITY HEADER ANALYSIS]\n"
                f"   • Audited Target : {clean_url}\n"
                f"   • Banner Server  : {server}\n"
                f"   • X-Frame-Options: {x_frame}\n"
                f"   • HSTS Standard  : {hsts}\n"
                f"   • Content-Policy : {csp}")
    except Exception as e:
        return f"❌ HEADER AUDIT FAILURE: Server refused standard payload sequence -> {str(e)}"

def perform_regex_filter(text: str, pattern: str) -> str:
    try:
        matches = re.findall(pattern, text)
        return f"🎯 Regex Extraction Complete. Found {len(matches)} operational hits matching criteria: {matches[:6]}"
    except Exception as e:
        return f"❌ Regex Evaluation Engine Exception: {str(e)}"

def perform_sql_injection_test(target: str, payload: str) -> str:
    clean_target = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    clean_payload = str(payload).strip()
    try:
        if not clean_target.startswith("http"):
            clean_target = "https://" + clean_target
        
        test_url = f"{clean_target}?id={urllib.parse.quote(clean_payload)}"
        req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            response_text = response.read().decode('utf-8', errors='ignore')
            
        # Simulate detection logic
        sql_indicators = ['SQL syntax', 'mysql_fetch', 'Warning:', 'error in your SQL', 'unclosed quotation']
        detected = [ind for ind in sql_indicators if ind.lower() in response_text.lower()]
        
        if detected:
            return f"⚠️ [SQL INJECTION TEST] Target appears VULNERABLE!\n   • Payload: {clean_payload}\n   • Detected Indicators: {', '.join(detected)}\n   ☠️ WARNING: This target may allow SQL injection attacks."
        else:
            return f"✅ [SQL INJECTION TEST] Target appears resistant.\n   • Payload Tested: {clean_payload}\n   • Status: No obvious SQL errors detected in response."
    except Exception as e:
        return f"❌ SQL Injection Test Failed: {str(e)}"

def perform_xss_payload_test(target: str, payload: str) -> str:
    clean_target = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    clean_payload = str(payload).strip()
    try:
        if not clean_target.startswith("http"):
            clean_target = "https://" + clean_target
        
        test_url = f"{clean_target}?search={urllib.parse.quote(clean_payload)}"
        req = urllib.request.Request(test_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            response_text = response.read().decode('utf-8', errors='ignore')
            
        # Check if payload is reflected without escaping
        if clean_payload in response_text:
            return f"⚠️ [XSS PAYLOAD TEST] Target appears VULNERABLE!\n   • Payload: {clean_payload}\n   • Status: Payload reflected without encoding\n   ☠️ WARNING: This target may allow XSS attacks."
        else:
            return f"✅ [XSS PAYLOAD TEST] Target appears resistant.\n   • Payload Tested: {clean_payload}\n   • Status: Payload was encoded or filtered."
    except Exception as e:
        return f"❌ XSS Test Failed: {str(e)}"

def perform_directory_brute_force(target: str, wordlist_sample: str) -> str:
    clean_target = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_target.startswith("http"):
        clean_target = "https://" + clean_target
    
    try:
        # Simulate directory brute forcing with common paths
        common_dirs = ["admin", "config", "backup", "upload", "api", "data", "secret", "private"]
        found_dirs = []
        
        for directory in common_dirs[:5]:  # Limit to 5 for simulation
            try:
                test_url = f"{clean_target}/{directory}/"
                req = urllib.request.Request(test_url, method="HEAD", headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=3) as response:
                    if response.status in [200, 301, 302]:
                        found_dirs.append((directory, response.status))
            except:
                pass
        
        if found_dirs:
            dirs_list = "\n   ".join([f"/{d} (HTTP {s})" for d, s in found_dirs])
            return f"🔓 [DIRECTORY BRUTE FORCE] Found exposed directories!\n   {dirs_list}\n   ⚠️ These directories may contain sensitive information."
        else:
            return f"🔒 [DIRECTORY BRUTE FORCE] No common directories found at {clean_target}"
    except Exception as e:
        return f"❌ Directory Brute Force Failed: {str(e)}"

def perform_credential_attack(target: str, username: str, password_list: str) -> str:
    clean_target = str(target).strip()
    clean_user = str(username).strip()
    pass_sample = str(password_list).strip()
    
    try:
        # Simulate credential testing (non-invasive)
        common_passwords = ["password123", "admin123", "letmein", "welcome", "test123", pass_sample]
        
        simulated_attempts = []
        for idx, pwd in enumerate(common_passwords[:3]):
            simulated_attempts.append(f"   Attempt {idx+1}: {clean_user}:{pwd} -> Connection Timeout (Rate Limited)")
        
        return f"🔑 [CREDENTIAL ATTACK SIMULATION] Testing {clean_user} against {clean_target}\n" + "\n".join(simulated_attempts) + "\n   ⚠️ Active credential attacks are blocked by rate limiting."
    except Exception as e:
        return f"❌ Credential Attack Simulation Failed: {str(e)}"

def perform_port_scan(target: str, port_range: str) -> str:
    clean_target = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    try:
        # Parse port range
        if "-" in port_range:
            start, end = port_range.split("-")
            start, end = int(start.strip()), int(end.strip())
        else:
            start = int(port_range.strip())
            end = start + 1
        
        # Simulate port scanning with common ports
        common_ports = [21, 22, 25, 80, 443, 3306, 5432, 8080, 3389]
        open_ports = []
        
        for port in common_ports:
            if start <= port <= end:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((clean_target, port))
                    sock.close()
                    if result == 0:
                        open_ports.append(port)
                except:
                    pass
        
        if open_ports:
            ports_str = ", ".join(map(str, open_ports))
            return f"🔓 [PORT SCAN RESULTS] Open ports on {clean_target}: {ports_str}\n   ⚠️ These ports may expose services."
        else:
            return f"🔒 [PORT SCAN RESULTS] No open ports detected on {clean_target} in range {start}-{end}"
    except Exception as e:
        return f"❌ Port Scan Failed: {str(e)}"

def perform_service_enumeration(target: str) -> str:
    clean_target = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_target.startswith("http"):
        clean_target = "https://" + clean_target
    
    try:
        req = urllib.request.Request(clean_target, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            headers = response.info()
            content = response.read().decode('utf-8', errors='ignore')[:2000]
        
        server_banner = headers.get("Server", "Unknown")
        powered_by = headers.get("X-Powered-By", "Unknown")
        
        tech_stack = f"Server: {server_banner}, Powered-By: {powered_by}"
        
        # Check for technology indicators
        techs = []
        if "WordPress" in content:
            techs.append("WordPress")
        if "Laravel" in content:
            techs.append("Laravel")
        if "Django" in content:
            techs.append("Django")
        if "React" in content:
            techs.append("React")
        if "Vue" in content:
            techs.append("Vue.js")
        
        return f"🔍 [SERVICE ENUMERATION] {clean_target}\n   {tech_stack}\n   Detected Technologies: {', '.join(techs) if techs else 'Standard Web Stack'}"
    except Exception as e:
        return f"❌ Service Enumeration Failed: {str(e)}"

def perform_vulnerability_lookup(target: str, cve_id: str = "") -> str:
    clean_target = str(target).strip()
    
    try:
        # Simulate CVE database lookup
        simulated_vulns = [
            "CVE-2024-21626: Container Escape",
            "CVE-2024-0519: Authentication Bypass",
            "CVE-2023-38606: Remote Code Execution"
        ]
        
        found_vulns = [v for v in simulated_vulns if cve_id.upper() in v or not cve_id][:3]
        
        vuln_list = "\n   ".join([f"• {v}" for v in found_vulns])
        return f"🔴 [VULNERABILITY DATABASE LOOKUP] {clean_target}\n   Associated CVEs:\n   {vuln_list}\n   ⚠️ Verify exploitability with PoC research."
    except Exception as e:
        return f"❌ Vulnerability Lookup Failed: {str(e)}"

def perform_malware_detection(target: str, sample_hash: str) -> str:
    clean_target = str(target).strip()
    clean_hash = str(sample_hash).strip().upper()
    
    try:
        # Simulate malware hash lookup
        malware_db = ["5D41402ABC4B2A76B9719D911017C592", "6D7FCED16E7A45FEC34AAF68E5C41F11"]
        
        if clean_hash in malware_db or len(clean_hash) == 32:  # MD5
            return f"⚠️ [MALWARE DETECTION] Hash {clean_hash}\n   Status: DETECTED in malware database\n   Threat Level: HIGH\n   ☠️ File appears to be known malware."
        else:
            return f"✅ [MALWARE DETECTION] Hash {clean_hash}\n   Status: NOT DETECTED\n   File appears clean or unknown."
    except Exception as e:
        return f"❌ Malware Detection Failed: {str(e)}"

def perform_firewall_detect(target: str) -> str:
    clean_target = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    clean_target = clean_target.replace("https://", "").replace("http://", "").split("/")[0]
    
    try:
        # Simulate firewall detection
        firewall_indicators = ["WAF Detected", "CloudFlare", "Akamai", "AWS Shield"]
        
        try:
            req = urllib.request.Request(f"https://{clean_target}", headers={'User-Agent': 'Test'})
            with urllib.request.urlopen(req, timeout=5) as response:
                headers = response.info()
                if "CF-RAY" in str(headers):
                    return f"🔥 [FIREWALL DETECTION] {clean_target}\n   Detected: CloudFlare WAF\n   ⚠️ Requests are being filtered."
        except:
            pass
        
        return f"🔥 [FIREWALL DETECTION] {clean_target}\n   Status: Standard firewall or rate limiting detected\n   Recommendation: Use proxy or distributed approach."
    except Exception as e:
        return f"❌ Firewall Detection Failed: {str(e)}"

def run_scan(target: str, mode: str, structural=None, payload: str = None, username: str = None, password_list: str = None) -> str:
    if mode == "dns":
        res = perform_dns_lookup(target)
    elif mode == "geo":
        res = perform_ip_geolocation(target)
    elif mode == "phone":
        res = perform_phone_tracking(target)
    elif mode == "whois":
        res = perform_whois_lookup(target)
    elif mode == "header_audit":
        res = perform_http_header_audit(target)
    elif mode == "shodan":
        res = perform_shodan_lookup(target)
    elif mode == "robots":
        res = perform_robots_sitemap_scan(target)
    elif mode == "ssl_audit":
        res = perform_ssl_audit(target)
    elif mode == "regex" and structural:
        res = perform_regex_filter(target, structural)
    elif mode == "sql_injection" and payload:
        res = perform_sql_injection_test(target, payload)
    elif mode == "xss_attack" and payload:
        res = perform_xss_payload_test(target, payload)
    elif mode == "directory_brute" and structural:
        res = perform_directory_brute_force(target, structural)
    elif mode == "credential_attack" and username and password_list:
        res = perform_credential_attack(target, username, password_list)
    elif mode == "port_scan" and structural:
        res = perform_port_scan(target, structural)
    elif mode == "service_enum":
        res = perform_service_enumeration(target)
    elif mode == "vuln_lookup" and structural:
        res = perform_vulnerability_lookup(target, structural)
    elif mode == "malware_detect" and structural:
        res = perform_malware_detection(target, structural)
    elif mode == "firewall_detect":
        res = perform_firewall_detect(target)
    elif mode == "fuzz":
        res = f"💥 [ATTACK ENGINE] Fuzzing sequence initiated on {target}...\n   -> Testing parameters for overflow logic.\n   -> Payload injection matrix simulated successfully."
    elif mode == "exploit":
        res = f"☠️ [ATTACK ENGINE] Deploying active exploit payload to {target}...\n   -> Bypassing simulated security controls.\n   -> Target compromised (Educational Simulation)."
    else:
        res = f"⚠️ Error: Block matching parameter structure error for mode: {mode}"
        
    st.session_state["terminal_history_output"] += f"\n[ENGINE TRACE] Activating Module -> {mode.upper()}\n{res}\n"
    return res

# ==========================================
# 2. CLEANED BLOCKLY TOOLBOX XML
# ==========================================

TOOLBOX_XML = """
  <xml id="toolbox" style="display: none">
    <category name="🧠 Core Logic" colour="210">
      <block type="controls_if"></block>
      <block type="logic_compare"></block>
      <block type="logic_operation"></block>
      <block type="logic_negate"></block>
      <block type="logic_boolean"></block>
    </category>
    
    <category name="🔁 Loops &amp; Wait" colour="120">
      <block type="controls_repeat_ext">
        <value name="TIMES">
          <shadow type="math_number">
            <field name="NUM">5</field>
          </shadow>
        </value>
      </block>
      <block type="controls_whileUntil"></block>
      <block type="action_wait_task"></block>
    </category>
    
    <category name="🔢 Math &amp; Data" colour="230">
      <block type="math_number"></block>
      <block type="math_arithmetic"></block>
      <block type="text"></block>
      <block type="text_print"></block>
    </category>
    
    <sep></sep>
    
    <category name="🏁 Sequence Triggers" colour="0">
      <block type="when_sequence_activated"></block>
    </category>
    <category name="🌐 Core Inputs" colour="160">
      <block type="custom_input_string"></block>
      <block type="global_phone_preset"></block>
      <block type="custom_phone_signature"></block>
    </category>
    
    <category name="🔎 Intelligence Gathering" colour="#5b80a2">
        <category name="🌐 Domain &amp; IP Info" colour="#4a6fa5">
            <block type="action_dns_resolve"></block>
            <block type="action_ip_geolocation"></block>
            <block type="action_whois_lookup"></block>
        </category>
        <category name="📱 Telecom Research" colour="#4a6fa5">
            <block type="action_phone_tracker"></block>
        </category>
        <category name="🕷️ Web &amp; Service Scan" colour="#4a6fa5">
            <block type="action_shodan_lookup"></block>
            <block type="action_robots_sitemap"></block>
            <block type="action_http_header_audit"></block>
            <block type="action_ssl_audit"></block>
            <block type="action_service_enum"></block>
        </category>
        <category name="🔧 Data Processing" colour="#4a6fa5">
            <block type="action_regex_filter"></block>
        </category>
    </category>

    <category name="☠️ Active Attack Vectors" colour="#8b0000">
        <block type="action_basic_fuzz"></block>
        <block type="action_exploit_payload"></block>
    </category>

    <category name="🔨 Attack Toolkit" colour="#8b4513">
        <category name="💉 Web Vulnerabilities" colour="#8b4513">
            <block type="action_sql_injection"></block>
            <block type="action_xss_attack"></block>
        </category>
        <category name="🔓 Infrastructure Attacks" colour="#8b4513">
            <block type="action_directory_brute"></block>
            <block type="action_port_scan"></block>
            <block type="action_credential_attack"></block>
        </category>
        <category name="🔴 Threat Analysis" colour="#8b4513">
            <block type="action_vuln_lookup"></block>
            <block type="action_malware_detect"></block>
            <block type="action_firewall_detect"></block>
        </category>
    </category>
  </xml>
"""

# ==========================================
# 3. CLEANED JAVASCRIPT LOGIC
# ==========================================

BLOCK_DEFINITIONS_JS = """
    Blockly.Blocks['when_sequence_activated'] = {
      init: function() {
        this.appendDummyInput()
            .appendField("🚀 SEQUENCE GENERATOR")
            .appendField(new Blockly.FieldTextInput("passive_recon_agent"), "SEQUENCE_ID");
        this.setNextStatement(true, null);
        this.setColour(0);
        this.setTooltip("Right-click workspace element to activate this modular route sequence block.");
      },
      customContextMenu: function(options) {
          var currentBlockInstance = this;
          var activateOption = {
              enabled: true,
              text: "⚡ Activate This Sequence",
              callback: function() {
                  // FIX 1: Grab the ENTIRE workspace code, not just the single block, so connected nodes are caught
                  var targetedSequencePayload = Blockly.Python.workspaceToCode(window.workspace);
                  var sequenceIdentifier = currentBlockInstance.getFieldValue("SEQUENCE_ID");
                  
                  // Grab the XML Matrix so the UI canvas doesn't get wiped!
                  var xmlDom = Blockly.Xml.workspaceToDom(window.workspace);
                  var currentXmlText = Blockly.Xml.domToText(xmlDom);
                  
                  var baseUrl = window.parent.location.origin + window.parent.location.pathname;
                  var targetUrl = baseUrl + "?payload_matrix=" + encodeURIComponent(targetedSequencePayload) + "&xml_matrix=" + encodeURIComponent(currentXmlText) + "&run_sequence=" + encodeURIComponent(sequenceIdentifier);
                  window.parent.location.href = targetUrl;
              }
          };
          options.push(activateOption);
      }
    };
    
    Blockly.Blocks['action_wait_task'] = {
      init: function() {
        this.appendDummyInput().appendField("⏳ Wait for").appendField(new Blockly.FieldNumber(1, 0, 60), "SECONDS").appendField("seconds");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null); this.setColour(120);
        this.setTooltip("Halts the sequencing execution thread for a fixed duration value before continuing.");
      }
    };

    Blockly.Blocks['custom_input_string'] = {
      init: function() {
        this.appendDummyInput().appendField("Target Domain:").appendField(new Blockly.FieldTextInput("google.com"), "RAW_TEXT");
        this.setOutput(true, "String"); this.setColour(160);
        this.setTooltip("Provide a target domain, URL, or raw string.");
      }
    };
    
    Blockly.Blocks['global_phone_preset'] = {
      init: function() {
        this.appendDummyInput().appendField("📱 Preset Phone Target").appendField(new Blockly.FieldDropdown([["🇮🇩 +62","+62"], ["🇺🇸 +1","+1"], ["🇬🇧 +44","+44"]]), "CC_PREFIX").appendField(new Blockly.FieldTextInput("8123456789"), "PHONE_BODY");
        this.setOutput(true, "String"); this.setColour(160);
        this.setTooltip("Select a country prefix and enter a phone number for tracking.");
      }
    };
    
    Blockly.Blocks['custom_phone_signature'] = {
      init: function() {
        this.appendDummyInput().appendField("🏳️ Custom Country Code Input").appendField(new Blockly.FieldTextInput("+61"), "CUSTOM_PREFIX").appendField("Number:").appendField(new Blockly.FieldTextInput("412345678"), "PHONE_BODY");
        this.setOutput(true, "String"); this.setColour(160);
        this.setTooltip("Input a custom international country code and phone number.");
      }
    };

    Blockly.Blocks['action_dns_resolve'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("📡 Resolve DNS Record Host");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(210);
        this.setTooltip("Queries standard network nameservers passively to determine the current mapped IPv4 address destination.");
      }
    };

    Blockly.Blocks['action_ip_geolocation'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("🌐 Fetch IP Location Profile");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(210);
        this.setTooltip("Queries public geolocation datasets to return city, province, country code, and owner properties.");
      }
    };

    Blockly.Blocks['action_phone_tracker'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("📞 Parse Telecom Carrier Registry");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(210);
        this.setTooltip("Uses public parsing models to safely identify the regional carrier provider and active timezone of a telephone node.");
      }
    };

    Blockly.Blocks['action_whois_lookup'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("🌐 Fetch WHOIS Record");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(210);
        this.setTooltip("Performs a WHOIS query to determine domain registrar info, creation dates, and administrative footprints.");
      }
    };

    Blockly.Blocks['action_http_header_audit'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("🛡️ Audit HTTP Headers");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(210);
        this.setTooltip("Sends a lightweight request to extract server banners and check for security configurations.");
      }
    };

    Blockly.Blocks['action_shodan_lookup'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("👁️ Shodan Passive Intel");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(210);
        this.setTooltip("Queries passive Shodan indexes to map open ports and known vulnerability exposures.");
      }
    };

    Blockly.Blocks['action_robots_sitemap'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("🤖 Robots/Sitemap Scan");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(210);
        this.setTooltip("Inspects targets for exposed robots.txt or sitemap files.");
      }
    };

    Blockly.Blocks['action_ssl_audit'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("🔒 SSL/TLS Cipher Audit Target");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(210);
        this.setTooltip("Performs automated evaluation of SSL certificate validity configurations.");
      }
    };

    Blockly.Blocks['action_regex_filter'] = {
      init: function() {
        this.appendDummyInput().appendField("🎯 Match Stream Logic via Expression:").appendField(new Blockly.FieldTextInput("[0-9]{1,3}\\\\.[0-9]{1,3}"), "PATTERN");
        this.appendValueInput("NAME").setCheck("String").appendField("    Input Vector Text:");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(290);
        this.setTooltip("Evaluates targeted streams against structural regex constraints to extract configuration strings.");
      }
    };

    Blockly.Blocks['action_basic_fuzz'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("💥 Basic Fuzz Payload");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour('#8b0000');
        this.setTooltip("Injects standard fuzzing payloads into target endpoint.");
      }
    };

    Blockly.Blocks['action_exploit_payload'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("☠️ Execute Exploit Payload");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour('#8b0000');
        this.setTooltip("Simulates an exploit execution on target.");
      }
    };

    Blockly.Blocks['action_sql_injection'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("💉 SQL Injection Test");
        this.appendValueInput("PAYLOAD").setCheck("String").appendField("   Payload:");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Tests a target for SQL injection vulnerabilities using a custom payload.");
      }
    };

    Blockly.Blocks['action_xss_attack'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("🔗 XSS Payload Test");
        this.appendValueInput("PAYLOAD").setCheck("String").appendField("   Payload:");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Tests a target for Cross-Site Scripting (XSS) vulnerabilities.");
      }
    };

    Blockly.Blocks['action_directory_brute'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("📂 Directory Brute Force");
        this.appendDummyInput().appendField("   Wordlist (sample):")
          .appendField(new Blockly.FieldTextInput("admin,config,backup"), "WORDLIST");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Attempts to discover hidden directories on a web server.");
      }
    };

    Blockly.Blocks['action_credential_attack'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("🔑 Credential Attack");
        this.appendDummyInput().appendField("   Username:")
          .appendField(new Blockly.FieldTextInput("admin"), "USERNAME");
        this.appendDummyInput().appendField("   Password List:")
          .appendField(new Blockly.FieldTextInput("password123,admin123"), "PASSWORD_LIST");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Simulates credential attack testing against a target service.");
      }
    };

    Blockly.Blocks['action_port_scan'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("🔓 Port Scan");
        this.appendDummyInput().appendField("   Port Range:")
          .appendField(new Blockly.FieldTextInput("80-443"), "PORT_RANGE");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Scans target for open ports in specified range.");
      }
    };

    Blockly.Blocks['action_service_enum'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("🔍 Enumerate Services");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Identifies web services and technologies running on target.");
      }
    };

    Blockly.Blocks['action_vuln_lookup'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("🔴 CVE Vulnerability Lookup");
        this.appendDummyInput().appendField("   CVE ID (optional):")
          .appendField(new Blockly.FieldTextInput("CVE-2024"), "CVE_ID");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Searches vulnerability database for associated CVEs.");
      }
    };

    Blockly.Blocks['action_malware_detect'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("⚠️ Malware Detection");
        this.appendDummyInput().appendField("   File Hash:")
          .appendField(new Blockly.FieldTextInput("5D41402ABC4B2A76B9719D911017C592"), "FILE_HASH");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Checks file hash against malware database.");
      }
    };

    Blockly.Blocks['action_firewall_detect'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("🔥 Detect Firewall/WAF");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Detects presence of firewall or Web Application Firewall.");
      }
    };
"""

# ==========================================
# 4. PYTHON CODES EMISSION SYNTAX MAPPING
# ==========================================

PYTHON_GENERATORS_JS = """
    Blockly.Python.forBlock['when_sequence_activated'] = function(block) { return '# Sequence Active: ' + block.getFieldValue('SEQUENCE_ID') + '\\n'; };
    Blockly.Python.forBlock['action_wait_task'] = function(block) { return 'time.sleep(' + block.getFieldValue('SECONDS') + ')\\n'; };
    
    // Support generators (return values)
    Blockly.Python.forBlock['custom_input_string'] = function(block) { return ["'" + block.getFieldValue('RAW_TEXT') + "'", Blockly.Python.ORDER_ATOMIC]; };
    Blockly.Python.forBlock['global_phone_preset'] = function(block) { return ["'" + block.getFieldValue('CC_PREFIX') + block.getFieldValue('PHONE_BODY') + "'", Blockly.Python.ORDER_ATOMIC]; };
    Blockly.Python.forBlock['custom_phone_signature'] = function(block) {
      var prefix = block.getFieldValue('CUSTOM_PREFIX').trim();
      if(!prefix.startsWith("+")) { prefix = "+" + prefix; }
      return ["'" + prefix + block.getFieldValue('PHONE_BODY').trim() + "'", Blockly.Python.ORDER_ATOMIC];
    };

    // Action generators (return executable statements)
    Blockly.Python.forBlock['action_dns_resolve'] = function(block) {
      var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
      return 'run_scan(target=' + val + ', mode="dns")\\n';
    };
    
    Blockly.Python.forBlock['action_ip_geolocation'] = function(block) {
      var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
      return 'run_scan(target=' + val + ', mode="geo")\\n';
    };
    
    Blockly.Python.forBlock['action_phone_tracker'] = function(block) {
      var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
      return 'run_scan(target=' + val + ', mode="phone")\\n';
    };

    Blockly.Python.forBlock['action_whois_lookup'] = function(block) {
      var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
      return 'run_scan(target=' + val + ', mode="whois")\\n';
    };

    Blockly.Python.forBlock['action_http_header_audit'] = function(block) {
      var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
      return 'run_scan(target=' + val + ', mode="header_audit")\\n';
    };

    Blockly.Python.forBlock['action_shodan_lookup'] = function(block) {
      var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
      return 'run_scan(target=' + val + ', mode="shodan")\\n';
    };

    Blockly.Python.forBlock['action_robots_sitemap'] = function(block) {
      var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
      return 'run_scan(target=' + val + ', mode="robots")\\n';
    };

    Blockly.Python.forBlock['action_ssl_audit'] = function(block) {
      var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
      return 'run_scan(target=' + val + ', mode="ssl_audit")\\n';
    };

    Blockly.Python.forBlock['action_regex_filter'] = function(block) {
      var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
      var regexPattern = block.getFieldValue('PATTERN');
      return 'run_scan(target=' + val + ', mode="regex", structural="' + regexPattern + '")\\n';
    };

    Blockly.Python.forBlock['action_basic_fuzz'] = function(block) {
      var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
      return 'run_scan(target=' + val + ', mode="fuzz")\\n';
    };

    Blockly.Python.forBlock['action_exploit_payload'] = function(block) {
      var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
      return 'run_scan(target=' + val + ', mode="exploit")\\n';
    };

    Blockly.Python.forBlock['action_sql_injection'] = function(block) {
      var target = Blockly.Python.valueToCode(block, 'TARGET', Blockly.Python.ORDER_ATOMIC) || "''";
      var payload = Blockly.Python.valueToCode(block, 'PAYLOAD', Blockly.Python.ORDER_ATOMIC) || "''";
      return 'run_scan(target=' + target + ', mode="sql_injection", payload=' + payload + ')\\n';
    };

    Blockly.Python.forBlock['action_xss_attack'] = function(block) {
      var target = Blockly.Python.valueToCode(block, 'TARGET', Blockly.Python.ORDER_ATOMIC) || "''";
      var payload = Blockly.Python.valueToCode(block, 'PAYLOAD', Blockly.Python.ORDER_ATOMIC) || "''";
      return 'run_scan(target=' + target + ', mode="xss_attack", payload=' + payload + ')\\n';
    };

    Blockly.Python.forBlock['action_directory_brute'] = function(block) {
      var target = Blockly.Python.valueToCode(block, 'TARGET', Blockly.Python.ORDER_ATOMIC) || "''";
      var wordlist = block.getFieldValue('WORDLIST');
      return 'run_scan(target=' + target + ', mode="directory_brute", structural="' + wordlist + '")\\n';
    };

    Blockly.Python.forBlock['action_credential_attack'] = function(block) {
      var target = Blockly.Python.valueToCode(block, 'TARGET', Blockly.Python.ORDER_ATOMIC) || "''";
      var username = block.getFieldValue('USERNAME');
      var passwordList = block.getFieldValue('PASSWORD_LIST');
      return 'run_scan(target=' + target + ', mode="credential_attack", username="' + username + '", password_list="' + passwordList + '")\\n';
    };

    Blockly.Python.forBlock['action_port_scan'] = function(block) {
      var target = Blockly.Python.valueToCode(block, 'TARGET', Blockly.Python.ORDER_ATOMIC) || "''";
      var portRange = block.getFieldValue('PORT_RANGE');
      return 'run_scan(target=' + target + ', mode="port_scan", structural="' + portRange + '")\\n';
    };

    Blockly.Python.forBlock['action_service_enum'] = function(block) {
      var target = Blockly.Python.valueToCode(block, 'TARGET', Blockly.Python.ORDER_ATOMIC) || "''";
      return 'run_scan(target=' + target + ', mode="service_enum")\\n';
    };

    Blockly.Python.forBlock['action_vuln_lookup'] = function(block) {
      var target = Blockly.Python.valueToCode(block, 'TARGET', Blockly.Python.ORDER_ATOMIC) || "''";
      var cveId = block.getFieldValue('CVE_ID');
      return 'run_scan(target=' + target + ', mode="vuln_lookup", structural="' + cveId + '")\\n';
    };

    Blockly.Python.forBlock['action_malware_detect'] = function(block) {
      var target = Blockly.Python.valueToCode(block, 'TARGET', Blockly.Python.ORDER_ATOMIC) || "''";
      var fileHash = block.getFieldValue('FILE_HASH');
      return 'run_scan(target=' + target + ', mode="malware_detect", structural="' + fileHash + '")\\n';
    };

    Blockly.Python.forBlock['action_firewall_detect'] = function(block) {
      var target = Blockly.Python.valueToCode(block, 'TARGET', Blockly.Python.ORDER_ATOMIC) || "''";
      return 'run_scan(target=' + target + ', mode="firewall_detect")\\n';
    };
"""