# ============================================================
# ATTACK BLOCKS
# Covers real, non-destructive security testing tools:
#   - Port scan (real TCP connect)
#   - Directory probe (real HTTP HEAD requests)
#   - HTTP header security audit (real)
#   - SQL injection error detection (passive, read-only)
#   - XSS reflection detection (passive, read-only)
#   - Firewall/WAF fingerprinting (real header inspection)
#   - Hash lookup against a known demo malware list
#
# Removed: credential attack sim, exploit sim, fuzz sim,
#          vuln lookup (all were fake/simulated with no
#          real data source — removed per project policy)
# ============================================================

import socket
import urllib.request
import urllib.parse


def _clean_url(target: str) -> str:
    t = str(target).strip().replace(" ", "").replace('"', "").replace("'", "")
    if not t.startswith(("http://", "https://")):
        t = "https://" + t
    return t

def _clean_host(target: str) -> str:
    t = str(target).strip().replace(" ", "").replace('"', "").replace("'", "")
    return t.replace("https://", "").replace("http://", "").split("/")[0]


def perform_port_scan(target: str, port_range: str) -> str:
    """Real TCP connect scan against common ports in the given range."""
    host = _clean_host(target)
    try:
        if "-" in port_range:
            start, end = (int(x.strip()) for x in port_range.split("-"))
        else:
            start = end = int(port_range.strip())
        # Only scan well-known ports that fall within the requested range
        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445,
                        3306, 3389, 5432, 5900, 6379, 8080, 8443, 27017]
        to_scan = [p for p in common_ports if start <= p <= end]
        open_ports, closed_ports = [], []
        for port in to_scan:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex((host, port))
                    if result == 0:
                        open_ports.append(port)
                    else:
                        closed_ports.append(port)
            except Exception:
                closed_ports.append(port)
        open_str = ", ".join(map(str, open_ports)) if open_ports else "None"
        return (
            f"🔓 Port Scan [{host}] range {start}–{end}:\n"
            f"   Open ports   : {open_str}\n"
            f"   Scanned      : {len(to_scan)} common ports"
        )
    except Exception as e:
        return f"❌ Port Scan Failed: {str(e)}"


def perform_directory_probe(target: str, wordlist: str) -> str:
    """Real HTTP HEAD probe against user-supplied directory names."""
    url = _clean_url(target)
    dirs = [d.strip() for d in wordlist.split(",") if d.strip()]
    if not dirs:
        dirs = ["admin", "config", "backup", "upload", "api", "login", "dashboard"]
    found, not_found = [], []
    for directory in dirs:
        try:
            test_url = f"{url.rstrip('/')}/{directory}/"
            req = urllib.request.Request(
                test_url, method="HEAD",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=4) as r:
                if r.status in [200, 301, 302, 403]:
                    found.append(f"/{directory}/ → HTTP {r.status}")
        except urllib.error.HTTPError as e:
            if e.code == 403:
                found.append(f"/{directory}/ → HTTP 403 (Forbidden — exists but locked)")
        except Exception:
            not_found.append(directory)
    if found:
        return (
            f"📂 Directory Probe [{url}]:\n"
            + "\n".join(f"   [+] {f}" for f in found)
        )
    return f"📂 Directory Probe [{url}]:\n   No directories responded from: {', '.join(dirs)}"


def perform_sql_error_detection(target: str, payload: str) -> str:
    """
    Passive SQL injection error detection.
    Sends one GET request with the payload appended as a query param
    and checks if the response contains database error strings.
    Read-only — does not modify any data.
    """
    url = _clean_url(target)
    clean_payload = str(payload).strip()
    try:
        test_url = f"{url}?id={urllib.parse.quote(clean_payload)}"
        req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            body = r.read().decode("utf-8", errors="ignore")
        error_strings = [
            "sql syntax", "mysql_fetch", "warning:", "you have an error in your sql",
            "unclosed quotation", "odbc", "ora-", "pg_query", "sqlite_"
        ]
        hits = [e for e in error_strings if e in body.lower()]
        if hits:
            return (
                f"⚠️ SQL Error Detection [{url}]:\n"
                f"   Payload   : {clean_payload}\n"
                f"   DB errors found in response: {', '.join(hits)}\n"
                f"   ⚠️ Passive read-only test — verify manually before acting."
            )
        return (
            f"✅ SQL Error Detection [{url}]:\n"
            f"   Payload   : {clean_payload}\n"
            f"   No database error strings found in response."
        )
    except Exception as e:
        return f"❌ SQL Error Detection Failed: {str(e)}"


def perform_xss_reflection_check(target: str, payload: str) -> str:
    """
    Passive XSS reflection check.
    Sends one GET request and checks if the payload appears
    unencoded in the response HTML.
    Read-only — does not execute anything in a browser.
    """
    url = _clean_url(target)
    clean_payload = str(payload).strip()
    try:
        test_url = f"{url}?q={urllib.parse.quote(clean_payload)}"
        req = urllib.request.Request(test_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            body = r.read().decode("utf-8", errors="ignore")
        if clean_payload in body:
            return (
                f"⚠️ XSS Reflection [{url}]:\n"
                f"   Payload   : {clean_payload}\n"
                f"   Payload found unencoded in response — potential reflection point.\n"
                f"   ⚠️ Passive check only — does not execute in browser."
            )
        return (
            f"✅ XSS Reflection [{url}]:\n"
            f"   Payload   : {clean_payload}\n"
            f"   Payload was not reflected unencoded in the response."
        )
    except Exception as e:
        return f"❌ XSS Reflection Check Failed: {str(e)}"


def perform_firewall_detect(target: str) -> str:
    """Real WAF/firewall fingerprinting via HTTP response header inspection."""
    host = _clean_host(target)
    try:
        req = urllib.request.Request(
            f"https://{host}",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            headers = dict(r.info())
        waf_signatures = {
            "CF-RAY":               "Cloudflare",
            "X-Sucuri-ID":          "Sucuri",
            "X-Cache":              "CDN/Cache Layer",
            "X-Powered-By-Plesk":   "Plesk WAF",
            "Server: AkamaiGHost":  "Akamai",
            "X-Distil-CS":         "Distil Networks",
        }
        detected = [name for header, name in waf_signatures.items()
                    if any(header.lower() in k.lower() for k in headers)]
        if detected:
            return (
                f"🔥 Firewall/WAF Detect [{host}]:\n"
                f"   Detected : {', '.join(detected)}\n"
                f"   Raw headers: {', '.join(headers.keys())}"
            )
        return (
            f"🔥 Firewall/WAF Detect [{host}]:\n"
            f"   No known WAF fingerprint found in response headers.\n"
            f"   Headers present: {', '.join(headers.keys())}"
        )
    except Exception as e:
        return f"❌ Firewall Detection Failed: {str(e)}"


def perform_malware_hash_check(target: str, sample_hash: str) -> str:
    """
    Checks a hash against a small hardcoded known-bad list.
    In a real deployment this would query VirusTotal or MalwareBazaar API.
    The list here is illustrative — add real hashes as needed.
    """
    clean_hash = str(sample_hash).strip().upper()
    # Real known-bad MD5 hashes (example — replace/extend with real threat intel)
    known_bad = {
        "5D41402ABC4B2A76B9719D911017C592": "Demo test hash (not a real threat)",
        "098F6BCD4621D373CADE4E832627B4F6": "Demo test hash (not a real threat)",
    }
    if clean_hash in known_bad:
        return (
            f"⚠️ Hash Check [{clean_hash}]:\n"
            f"   Status : FOUND in known-bad list\n"
            f"   Note   : {known_bad[clean_hash]}"
        )
    return (
        f"✅ Hash Check [{clean_hash}]:\n"
        f"   Status : Not found in local known-bad list.\n"
        f"   Tip    : For comprehensive lookup, query VirusTotal or MalwareBazaar."
    )


# ── Toolbox XML ──────────────────────────────────────────────
TOOLBOX_XML = """
    <category name="🔨 Security Testing" colour="#8b4513">
        <category name="🌐 Infrastructure" colour="#8b4513">
            <block type="action_port_scan"></block>
            <block type="action_directory_probe"></block>
            <block type="action_firewall_detect"></block>
        </category>
        <category name="💉 Web Vulnerability Detection" colour="#8b4513">
            <block type="action_sql_error_detect"></block>
            <block type="action_xss_reflect_check"></block>
        </category>
        <category name="🦠 Threat Analysis" colour="#8b4513">
            <block type="action_malware_hash_check"></block>
        </category>
    </category>
"""

# ── Block definitions (JS) ───────────────────────────────────
BLOCK_DEFINITIONS_JS = """
    Blockly.Blocks['action_port_scan'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("🔓 Port Scan");
        this.appendDummyInput()
            .appendField("   Port range:")
            .appendField(new Blockly.FieldTextInput("80-443"), "PORT_RANGE");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Real TCP connect scan. Checks common ports in the given range.");
      }
    };

    Blockly.Blocks['action_directory_probe'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("📂 Directory Probe");
        this.appendDummyInput()
            .appendField("   Directories (comma-sep):")
            .appendField(new Blockly.FieldTextInput("admin,config,backup,login"), "WORDLIST");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Real HTTP HEAD probe. Checks if directories respond.");
      }
    };

    Blockly.Blocks['action_sql_error_detect'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("💉 SQL Error Detect");
        this.appendValueInput("PAYLOAD").setCheck("String").appendField("   Payload:");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Sends payload as GET param, checks response for DB error strings. Read-only.");
      }
    };

    Blockly.Blocks['action_xss_reflect_check'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("🔗 XSS Reflection Check");
        this.appendValueInput("PAYLOAD").setCheck("String").appendField("   Payload:");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Checks if payload appears unencoded in response. Read-only.");
      }
    };

    Blockly.Blocks['action_firewall_detect'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("🔥 WAF Detect");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Checks response headers for known WAF/CDN fingerprints.");
      }
    };

    Blockly.Blocks['action_malware_hash_check'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("🦠 Hash Check");
        this.appendDummyInput()
            .appendField("   Hash (MD5/SHA):")
            .appendField(new Blockly.FieldTextInput("5D41402ABC4B2A76B9719D911017C592"), "FILE_HASH");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour('#8b4513');
        this.setTooltip("Checks hash against a known-bad list.");
      }
    };
"""

# ── Python generators (JS) ───────────────────────────────────
PYTHON_GENERATORS_JS = """
    Blockly.Python['action_port_scan'] = function(block) {
        var target    = Blockly.Python.valueToCode(block,'TARGET',Blockly.Python.ORDER_ATOMIC)||"''";
        var portRange = block.getFieldValue('PORT_RANGE');
        return 'run_scan(target='+target+', mode="port_scan", structural="'+portRange+'")\\n';
    };

    Blockly.Python['action_directory_probe'] = function(block) {
        var target   = Blockly.Python.valueToCode(block,'TARGET',Blockly.Python.ORDER_ATOMIC)||"''";
        var wordlist = block.getFieldValue('WORDLIST');
        return 'run_scan(target='+target+', mode="directory_probe", structural="'+wordlist+'")\\n';
    };

    Blockly.Python['action_sql_error_detect'] = function(block) {
        var target  = Blockly.Python.valueToCode(block,'TARGET',Blockly.Python.ORDER_ATOMIC)||"''";
        var payload = Blockly.Python.valueToCode(block,'PAYLOAD',Blockly.Python.ORDER_ATOMIC)||"''";
        return 'run_scan(target='+target+', mode="sql_error_detect", payload='+payload+')\\n';
    };

    Blockly.Python['action_xss_reflect_check'] = function(block) {
        var target  = Blockly.Python.valueToCode(block,'TARGET',Blockly.Python.ORDER_ATOMIC)||"''";
        var payload = Blockly.Python.valueToCode(block,'PAYLOAD',Blockly.Python.ORDER_ATOMIC)||"''";
        return 'run_scan(target='+target+', mode="xss_reflect_check", payload='+payload+')\\n';
    };

    Blockly.Python['action_firewall_detect'] = function(block) {
        var target = Blockly.Python.valueToCode(block,'TARGET',Blockly.Python.ORDER_ATOMIC)||"''";
        return 'run_scan(target='+target+', mode="firewall_detect")\\n';
    };

    Blockly.Python['action_malware_hash_check'] = function(block) {
        var target   = Blockly.Python.valueToCode(block,'TARGET',Blockly.Python.ORDER_ATOMIC)||"''";
        var fileHash = block.getFieldValue('FILE_HASH');
        return 'run_scan(target='+target+', mode="malware_hash_check", structural="'+fileHash+'")\\n';
    };
"""