# ============================================================
# ATTACK BLOCKS
# Covers: SQL Injection, XSS, Directory Brute Force,
#         Port Scan, Credential Attack, Fuzz, Exploit,
#         Vulnerability Lookup, Malware Detection, Firewall Detect
#
# NOTE: All active-looking functions here are SIMULATIONS.
# They demonstrate what these tests look like conceptually
# but do not perform real attacks. They are educational demos.
# ============================================================

import socket
import urllib.request
import urllib.parse


# ── Helper ───────────────────────────────────────────────────

def _clean_url(target: str) -> str:
    t = str(target).strip().replace(" ", "").replace('"', "").replace("'", "")
    if not t.startswith(("http://", "https://")):
        t = "https://" + t
    return t

def _clean_host(target: str) -> str:
    t = str(target).strip().replace(" ", "").replace('"', "").replace("'", "")
    return t.replace("https://", "").replace("http://", "").split("/")[0]


# ── Python backend functions ──────────────────────────────────

def perform_sql_injection_test(target: str, payload: str) -> str:
    url = _clean_url(target)
    clean_payload = str(payload).strip()
    try:
        test_url = f"{url}?id={urllib.parse.quote(clean_payload)}"
        req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            body = response.read().decode("utf-8", errors="ignore")
        indicators = ["SQL syntax", "mysql_fetch", "Warning:", "error in your SQL",
                      "unclosed quotation"]
        detected = [i for i in indicators if i.lower() in body.lower()]
        if detected:
            return (
                f"⚠️ [SQL INJECTION TEST] Potential vulnerability detected!\n"
                f"   Payload    : {clean_payload}\n"
                f"   Indicators : {', '.join(detected)}\n"
                f"   ☠️ Educational finding only — verify manually."
            )
        return (
            f"✅ [SQL INJECTION TEST] No obvious indicators found.\n"
            f"   Payload : {clean_payload}\n"
            f"   Status  : Response did not reflect SQL error strings."
        )
    except Exception as e:
        return f"❌ SQL Injection Test Failed: {str(e)}"


def perform_xss_payload_test(target: str, payload: str) -> str:
    url = _clean_url(target)
    clean_payload = str(payload).strip()
    try:
        test_url = f"{url}?search={urllib.parse.quote(clean_payload)}"
        req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            body = response.read().decode("utf-8", errors="ignore")
        if clean_payload in body:
            return (
                f"⚠️ [XSS TEST] Payload reflected without encoding!\n"
                f"   Payload : {clean_payload}\n"
                f"   ☠️ Educational finding only — verify manually."
            )
        return (
            f"✅ [XSS TEST] Payload was encoded or filtered.\n"
            f"   Payload : {clean_payload}"
        )
    except Exception as e:
        return f"❌ XSS Test Failed: {str(e)}"


def perform_directory_brute_force(target: str, wordlist_sample: str) -> str:
    url = _clean_url(target)
    # Only tests a small hardcoded list — this is a demonstration, not a real brute force.
    common_dirs = ["admin", "config", "backup", "upload", "api"]
    found = []
    for directory in common_dirs:
        try:
            test_url = f"{url}/{directory}/"
            req = urllib.request.Request(test_url, method="HEAD",
                                         headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=3) as r:
                if r.status in [200, 301, 302]:
                    found.append((directory, r.status))
        except Exception:
            pass
    if found:
        dirs = "\n   ".join(f"/{d}  (HTTP {s})" for d, s in found)
        return (
            f"🔓 [DIRECTORY SCAN] Accessible paths on {url}:\n"
            f"   {dirs}\n"
            f"   ⚠️ These directories responded — review manually."
        )
    return f"🔒 [DIRECTORY SCAN] No common directories responded on {url}"


def perform_port_scan(target: str, port_range: str) -> str:
    host = _clean_host(target)
    try:
        if "-" in port_range:
            start, end = (int(x.strip()) for x in port_range.split("-"))
        else:
            start = end = int(port_range.strip())
        common_ports = [21, 22, 25, 80, 443, 3306, 5432, 8080, 3389]
        open_ports = []
        for port in common_ports:
            if start <= port <= end:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        sock.settimeout(1)
                        if sock.connect_ex((host, port)) == 0:
                            open_ports.append(port)
                except Exception:
                    pass
        if open_ports:
            return (
                f"🔓 [PORT SCAN] Open ports on {host}: {', '.join(map(str, open_ports))}\n"
                f"   ⚠️ These ports are actively responding."
            )
        return f"🔒 [PORT SCAN] No open ports found on {host} in range {start}–{end}"
    except Exception as e:
        return f"❌ Port Scan Failed: {str(e)}"


def perform_credential_attack(target: str, username: str, password_list: str) -> str:
    # This is a pure simulation — no real login attempts are made.
    clean_user = str(username).strip()
    attempts = [
        f"   Attempt 1: {clean_user}:password123  → Connection Timeout (Rate Limited)",
        f"   Attempt 2: {clean_user}:admin123      → Connection Timeout (Rate Limited)",
        f"   Attempt 3: {clean_user}:letmein       → Connection Timeout (Rate Limited)",
    ]
    return (
        f"🔑 [CREDENTIAL ATTACK SIMULATION] Target: {target} | User: {clean_user}\n"
        + "\n".join(attempts)
        + "\n   ⚠️ Simulation only — no real requests were made."
    )


def perform_vulnerability_lookup(target: str, cve_id: str = "") -> str:
    # Simulated CVE database — not a real NVD/MITRE query.
    sim_vulns = [
        "CVE-2024-21626: Container Escape (runc)",
        "CVE-2024-0519: Authentication Bypass",
        "CVE-2023-38606: Remote Code Execution",
    ]
    found = [v for v in sim_vulns if cve_id.upper() in v or not cve_id][:3]
    vuln_list = "\n   ".join(f"• {v}" for v in found)
    return (
        f"🔴 [VULNERABILITY LOOKUP — DEMO DATA] {target}\n"
        f"   {vuln_list}\n"
        f"   ⚠️ These are example CVEs, not a real scan result."
    )


def perform_malware_detection(target: str, sample_hash: str) -> str:
    clean_hash = str(sample_hash).strip().upper()
    # Only flag hashes that are actually in the demo list — not by length.
    demo_malware_db = {"5D41402ABC4B2A76B9719D911017C592"}
    if clean_hash in demo_malware_db:
        return (
            f"⚠️ [MALWARE DETECTION — DEMO] Hash: {clean_hash}\n"
            f"   Status      : Found in demo malware list\n"
            f"   Threat Level: HIGH (demo)\n"
            f"   ⚠️ This is a simulated result."
        )
    return (
        f"✅ [MALWARE DETECTION — DEMO] Hash: {clean_hash}\n"
        f"   Status: Not found in demo database."
    )


def perform_firewall_detect(target: str) -> str:
    host = _clean_host(target)
    try:
        req = urllib.request.Request(f"https://{host}",
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            headers = str(response.info())
        if "CF-RAY" in headers:
            return (
                f"🔥 [FIREWALL DETECT] {host}\n"
                f"   Detected: Cloudflare WAF\n"
                f"   Requests are being proxied and filtered."
            )
        return (
            f"🔥 [FIREWALL DETECT] {host}\n"
            f"   Status: No well-known WAF fingerprint detected in headers."
        )
    except Exception as e:
        return f"❌ Firewall Detection Failed: {str(e)}"


def perform_basic_fuzz(target: str) -> str:
    # Simulation only — no real fuzzing payloads sent.
    return (
        f"💥 [FUZZ SIMULATION] Target: {target}\n"
        f"   → Parameter overflow test: simulated\n"
        f"   → Boundary injection matrix: simulated\n"
        f"   ⚠️ This is an educational simulation only."
    )


def perform_exploit_simulation(target: str) -> str:
    # Simulation only — no real exploit is executed.
    return (
        f"☠️ [EXPLOIT SIMULATION] Target: {target}\n"
        f"   → Bypassing simulated security controls: simulated\n"
        f"   → Payload delivery: simulated\n"
        f"   ⚠️ This is an educational simulation only."
    )


# ── Toolbox XML ─────────────────────────────────────────────
TOOLBOX_XML = """
    <category name="🔨 Attack Toolkit" colour="#8b4513">
        <category name="💉 Web Vulnerabilities" colour="#8b4513">
            <block type="action_sql_injection"></block>
            <block type="action_xss_attack"></block>
        </category>
        <category name="🔓 Infrastructure" colour="#8b4513">
            <block type="action_directory_brute"></block>
            <block type="action_port_scan"></block>
            <block type="action_credential_attack"></block>
        </category>
        <category name="🔴 Threat Analysis" colour="#8b4513">
            <block type="action_vuln_lookup"></block>
            <block type="action_malware_detect"></block>
            <block type="action_firewall_detect"></block>
        </category>
        <category name="☠️ Simulation Payloads" colour="#8b0000">
            <block type="action_basic_fuzz"></block>
            <block type="action_exploit_payload"></block>
        </category>
    </category>
"""

# ── Block definitions (JS) ───────────────────────────────────
BLOCK_DEFINITIONS_JS = """
    Blockly.Blocks['action_sql_injection'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("💉 SQL Injection Test");
        this.appendValueInput("PAYLOAD").setCheck("String").appendField("   Payload:");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Tests a URL for SQL injection error indicators.");
      }
    };

    Blockly.Blocks['action_xss_attack'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("🔗 XSS Test");
        this.appendValueInput("PAYLOAD").setCheck("String").appendField("   Payload:");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Checks if a payload is reflected unescaped in the response.");
      }
    };

    Blockly.Blocks['action_directory_brute'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("📂 Directory Scan");
        this.appendDummyInput()
            .appendField("   Wordlist:")
            .appendField(new Blockly.FieldTextInput("admin,config,backup"), "WORDLIST");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Checks for common accessible directories on a web server.");
      }
    };

    Blockly.Blocks['action_port_scan'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("🔓 Port Scan");
        this.appendDummyInput()
            .appendField("   Port Range:")
            .appendField(new Blockly.FieldTextInput("80-443"), "PORT_RANGE");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Scans common ports in the specified range.");
      }
    };

    Blockly.Blocks['action_credential_attack'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("🔑 Credential Attack");
        this.appendDummyInput()
            .appendField("   Username:")
            .appendField(new Blockly.FieldTextInput("admin"), "USERNAME");
        this.appendDummyInput()
            .appendField("   Password List:")
            .appendField(new Blockly.FieldTextInput("password123,admin123"), "PASSWORD_LIST");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Simulates a credential attack — no real requests are made.");
      }
    };

    Blockly.Blocks['action_vuln_lookup'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("🔴 CVE Lookup");
        this.appendDummyInput()
            .appendField("   CVE ID (optional):")
            .appendField(new Blockly.FieldTextInput("CVE-2024"), "CVE_ID");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Returns example CVEs from a simulated database.");
      }
    };

    Blockly.Blocks['action_malware_detect'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("⚠️ Malware Detection");
        this.appendDummyInput()
            .appendField("   File Hash:")
            .appendField(new Blockly.FieldTextInput("5D41402ABC4B2A76B9719D911017C592"), "FILE_HASH");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Checks a hash against a small demo malware list.");
      }
    };

    Blockly.Blocks['action_firewall_detect'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("🔥 Firewall Detect");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Checks response headers for known WAF fingerprints.");
      }
    };

    Blockly.Blocks['action_basic_fuzz'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("💥 Basic Fuzz (Sim)");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour('#8b0000');
        this.setTooltip("Educational fuzzing simulation — no real payloads sent.");
      }
    };

    Blockly.Blocks['action_exploit_payload'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("☠️ Exploit (Sim)");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour('#8b0000');
        this.setTooltip("Educational exploit simulation — no real exploit is run.");
      }
    };
"""

# ── Python generators (JS) ───────────────────────────────────
PYTHON_GENERATORS_JS = """
    Blockly.Python['action_sql_injection'] = function(block) {
        var target  = Blockly.Python.valueToCode(block, 'TARGET', Blockly.Python.ORDER_ATOMIC) || "''";
        var payload = Blockly.Python.valueToCode(block, 'PAYLOAD', Blockly.Python.ORDER_ATOMIC) || "''";
        return 'run_scan(target=' + target + ', mode="sql_injection", payload=' + payload + ')\\n';
    };

    Blockly.Python['action_xss_attack'] = function(block) {
        var target  = Blockly.Python.valueToCode(block, 'TARGET', Blockly.Python.ORDER_ATOMIC) || "''";
        var payload = Blockly.Python.valueToCode(block, 'PAYLOAD', Blockly.Python.ORDER_ATOMIC) || "''";
        return 'run_scan(target=' + target + ', mode="xss_attack", payload=' + payload + ')\\n';
    };

    Blockly.Python['action_directory_brute'] = function(block) {
        var target   = Blockly.Python.valueToCode(block, 'TARGET', Blockly.Python.ORDER_ATOMIC) || "''";
        var wordlist = block.getFieldValue('WORDLIST');
        return 'run_scan(target=' + target + ', mode="directory_brute", structural="' + wordlist + '")\\n';
    };

    Blockly.Python['action_port_scan'] = function(block) {
        var target    = Blockly.Python.valueToCode(block, 'TARGET', Blockly.Python.ORDER_ATOMIC) || "''";
        var portRange = block.getFieldValue('PORT_RANGE');
        return 'run_scan(target=' + target + ', mode="port_scan", structural="' + portRange + '")\\n';
    };

    Blockly.Python['action_credential_attack'] = function(block) {
        var target   = Blockly.Python.valueToCode(block, 'TARGET', Blockly.Python.ORDER_ATOMIC) || "''";
        var username = block.getFieldValue('USERNAME');
        var passList = block.getFieldValue('PASSWORD_LIST');
        return 'run_scan(target=' + target + ', mode="credential_attack", username="' + username + '", password_list="' + passList + '")\\n';
    };

    Blockly.Python['action_vuln_lookup'] = function(block) {
        var target = Blockly.Python.valueToCode(block, 'TARGET', Blockly.Python.ORDER_ATOMIC) || "''";
        var cveId  = block.getFieldValue('CVE_ID');
        return 'run_scan(target=' + target + ', mode="vuln_lookup", structural="' + cveId + '")\\n';
    };

    Blockly.Python['action_malware_detect'] = function(block) {
        var target   = Blockly.Python.valueToCode(block, 'TARGET', Blockly.Python.ORDER_ATOMIC) || "''";
        var fileHash = block.getFieldValue('FILE_HASH');
        return 'run_scan(target=' + target + ', mode="malware_detect", structural="' + fileHash + '")\\n';
    };

    Blockly.Python['action_firewall_detect'] = function(block) {
        var target = Blockly.Python.valueToCode(block, 'TARGET', Blockly.Python.ORDER_ATOMIC) || "''";
        return 'run_scan(target=' + target + ', mode="firewall_detect")\\n';
    };

    Blockly.Python['action_basic_fuzz'] = function(block) {
        var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
        return 'run_scan(target=' + val + ', mode="fuzz")\\n';
    };

    Blockly.Python['action_exploit_payload'] = function(block) {
        var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
        return 'run_scan(target=' + val + ', mode="exploit")\\n';
    };
"""
