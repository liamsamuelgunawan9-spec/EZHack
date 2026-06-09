# ============================================================
# RECON BLOCKS
# Covers: DNS, GeoIP, WHOIS, Phone, SSL, Robots/Sitemap,
#         Shodan, HTTP Headers, Service Enumeration, Regex
# All functions are PASSIVE — no active attacks here.
# ============================================================

import socket
import json
import urllib.request
import urllib.parse
import re
import ssl

import phonenumbers
from phonenumbers import carrier, geocoder, timezone


# ── Helper: input sanitizers ─────────────────────────────────

def _clean_host(target: str) -> str:
    """Strip spaces/quotes, remove protocol prefix, take only the hostname."""
    t = str(target).strip().replace(" ", "").replace('"', "").replace("'", "")
    t = t.replace("https://", "").replace("http://", "").split("/")[0]
    return t

def _clean_url(target: str) -> str:
    """Ensure the target is a full URL with https:// prefix."""
    t = str(target).strip().replace(" ", "").replace('"', "").replace("'", "")
    if not t.startswith(("http://", "https://")):
        t = "https://" + t
    return t


# ── Python backend functions ──────────────────────────────────

def perform_dns_lookup(target: str) -> str:
    host = _clean_host(target)
    if not host:
        return "❌ ERROR: Target host missing!"
    if host.startswith("+") or (host.isdigit() and len(host) > 6):
        return perform_phone_tracking(host)
    try:
        ip_addr = socket.gethostbyname(host)
        return (
            f"📡 DNS Resolution successful for [{host}]\n"
            f"📍 Resolved IP Address: {ip_addr}"
        )
    except Exception as e:
        return f"❌ DNS Lookup Failed for '{host}': {str(e)}"


def perform_ip_geolocation(target: str) -> str:
    host = _clean_host(target)
    if not host:
        return "❌ ERROR: Geolocation target missing!"
    try:
        ip_addr = socket.gethostbyname(host)
        url = f"http://ip-api.com/json/{ip_addr}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
        if data.get("status") == "success":
            return (
                f"📍 IP Geolocation [{ip_addr}]:\n"
                f"   Country : {data.get('country')} ({data.get('countryCode')})\n"
                f"   Region  : {data.get('regionName')}\n"
                f"   City    : {data.get('city')}\n"
                f"   ISP     : {data.get('isp')}\n"
                f"   Coords  : {data.get('lat')}, {data.get('lon')}"
            )
        return f"⚠️ Geolocation API returned failure for [{ip_addr}]."
    except Exception as e:
        return f"❌ Geolocation Failed: {str(e)}"


def perform_phone_tracking(target: str) -> str:
    raw = str(target).strip().replace(" ", "").replace('"', "").replace("'", "")
    if not raw.startswith("+"):
        raw = "+" + raw
    try:
        parsed = phonenumbers.parse(raw, None)
        if not phonenumbers.is_valid_number(parsed):
            return f"❌ ERROR: '{raw}' is not a valid E.164 phone number."
        region   = geocoder.description_for_number(parsed, "en") or "Unknown"
        carrier_ = carrier.name_for_number(parsed, "en") or "Unknown Provider"
        tz_list  = timezone.time_zones_for_number(parsed)
        return (
            f"📱 Phone Lookup [{raw}]:\n"
            f"   Valid Format   : True\n"
            f"   Country        : {region}\n"
            f"   Network Carrier: {carrier_}\n"
            f"   Timezone       : {', '.join(tz_list)}"
        )
    except Exception as e:
        return f"❌ Phone Tracking Error: {str(e)}"


def perform_whois_lookup(target: str) -> str:
    host = _clean_host(target).lower()
    if not host:
        return "❌ ERROR: Target domain missing!"
    try:
        api_url = f"https://rdap.org/domain/{host}"
        req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as stream:
            data = json.loads(stream.read().decode())
        registrar = data.get("port43", "Unknown")
        creation_date = "Unknown"
        for event in data.get("events", []):
            if event.get("action") == "registration":
                creation_date = event.get("eventDate", "Unknown")
        return (
            f"🌐 WHOIS [{host}]:\n"
            f"   Registrar : {registrar}\n"
            f"   Created   : {creation_date}"
        )
    except Exception as e:
        return f"❌ WHOIS Lookup Failed: {str(e)}"


def perform_robots_sitemap_scan(target: str) -> str:
    url = _clean_url(target)
    report = f"🕸️ Robots/Sitemap scan for [{url}]:\n"
    try:
        req = urllib.request.Request(url.rstrip("/") + "/robots.txt",
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as r:
            lines = r.read().decode("utf-8", errors="ignore").split("\n")
        disallowed = [l for l in lines if l.lower().startswith("disallow:")]
        report += f"   [+] robots.txt found — {len(disallowed)} restricted paths\n"
        if disallowed:
            report += "       Sample:\n"
            report += "\n".join(f"       {d.strip()}" for d in disallowed[:4]) + "\n"
    except Exception:
        report += "   [-] robots.txt not found\n"
    try:
        req = urllib.request.Request(url.rstrip("/") + "/sitemap.xml",
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4):
            report += "   [+] sitemap.xml found\n"
    except Exception:
        report += "   [-] sitemap.xml not found\n"
    return report


def perform_ssl_audit(target: str) -> str:
    host = _clean_host(target)
    if not host:
        return "❌ ERROR: SSL audit target missing!"
    context = ssl.create_default_context()
    try:
        with socket.create_connection((host, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                cert   = ssock.getpeercert()
                cipher = ssock.cipher()
                version = ssock.version()
                issuer  = dict(x[0] for x in cert.get("issuer", []))
                subject = dict(x[0] for x in cert.get("subject", []))
                return (
                    f"🔒 SSL/TLS Audit [{host}]:\n"
                    f"   Protocol : {version}\n"
                    f"   Cipher   : {cipher[0]} ({cipher[2]} bits)\n"
                    f"   Issuer   : {issuer.get('organizationName', 'Unknown')}\n"
                    f"   Subject  : {subject.get('commonName', 'Unknown')}\n"
                    f"   Expires  : {cert.get('notAfter')}"
                )
    except Exception as e:
        return f"❌ SSL Handshake Failed: {str(e)}"


def perform_shodan_lookup(target: str) -> str:
    host = _clean_host(target)
    try:
        ip_addr = socket.gethostbyname(host)
        # NOTE: This is a simulation — no real Shodan API key is used.
        sim_ports = [80, 443, 22, 8080] if "example" in host else [80, 443]
        return (
            f"📡 Shodan Simulation [{ip_addr}]:\n"
            f"   [DEMO DATA — not a real Shodan query]\n"
            f"   Common open ports : {', '.join(map(str, sim_ports))}\n"
            f"   OS guess          : Linux 4.x/5.x"
        )
    except Exception as e:
        return f"❌ Shodan Lookup Failed: {str(e)}"


def perform_http_header_audit(target: str) -> str:
    url = _clean_url(target)
    try:
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            headers = response.info()
        server  = headers.get("Server", "Hidden/Not Disclosed")
        x_frame = headers.get("X-Frame-Options", "❌ MISSING (Clickjacking risk)")
        hsts    = headers.get("Strict-Transport-Security", "❌ MISSING (MITM risk)")
        csp     = headers.get("Content-Security-Policy", "❌ MISSING (XSS risk)")
        return (
            f"🛡️ HTTP Header Audit [{url}]:\n"
            f"   Server          : {server}\n"
            f"   X-Frame-Options : {x_frame}\n"
            f"   HSTS            : {hsts}\n"
            f"   Content-Policy  : {csp}"
        )
    except Exception as e:
        return f"❌ Header Audit Failed: {str(e)}"


def perform_service_enumeration(target: str) -> str:
    url = _clean_url(target)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            headers = response.info()
            content = response.read().decode("utf-8", errors="ignore")[:2000]
        server    = headers.get("Server", "Unknown")
        powered   = headers.get("X-Powered-By", "Unknown")
        techs = []
        for name, keyword in [("WordPress","WordPress"), ("Laravel","Laravel"),
                               ("Django","Django"), ("React","React"),
                               ("Vue.js","Vue")]:
            if keyword in content:
                techs.append(name)
        return (
            f"🔍 Service Enumeration [{url}]:\n"
            f"   Server     : {server}\n"
            f"   Powered-By : {powered}\n"
            f"   Detected   : {', '.join(techs) if techs else 'Standard web stack'}"
        )
    except Exception as e:
        return f"❌ Service Enumeration Failed: {str(e)}"


def perform_regex_filter(text: str, pattern: str) -> str:
    try:
        matches = re.findall(pattern, text)
        return f"🎯 Regex: found {len(matches)} match(es): {matches[:6]}"
    except Exception as e:
        return f"❌ Regex Error: {str(e)}"


# ── Toolbox XML ─────────────────────────────────────────────
TOOLBOX_XML = """
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
"""

# ── Block definitions (JS) ───────────────────────────────────
BLOCK_DEFINITIONS_JS = """
    Blockly.Blocks['action_dns_resolve'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("📡 Resolve DNS");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour(210);
        this.setTooltip("Resolves a domain name to its IP address.");
      }
    };

    Blockly.Blocks['action_ip_geolocation'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("🌐 IP Geolocation");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour(210);
        this.setTooltip("Returns city, country, ISP, and coordinates for an IP/domain.");
      }
    };

    Blockly.Blocks['action_phone_tracker'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("📞 Phone Lookup");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour(210);
        this.setTooltip("Identifies carrier and region for a phone number.");
      }
    };

    Blockly.Blocks['action_whois_lookup'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("🌐 WHOIS Lookup");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour(210);
        this.setTooltip("Fetches domain registration info via RDAP.");
      }
    };

    Blockly.Blocks['action_robots_sitemap'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("🤖 Robots/Sitemap");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour(210);
        this.setTooltip("Checks for robots.txt and sitemap.xml files.");
      }
    };

    Blockly.Blocks['action_ssl_audit'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("🔒 SSL Audit");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour(210);
        this.setTooltip("Checks SSL/TLS certificate details and cipher strength.");
      }
    };

    Blockly.Blocks['action_shodan_lookup'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("👁️ Shodan Lookup");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour(210);
        this.setTooltip("Simulates a Shodan passive intel lookup (demo data).");
      }
    };

    Blockly.Blocks['action_http_header_audit'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("🛡️ HTTP Headers");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour(210);
        this.setTooltip("Checks security headers like HSTS, CSP, X-Frame-Options.");
      }
    };

    Blockly.Blocks['action_service_enum'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("🔍 Service Enum");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour(210);
        this.setTooltip("Identifies web technologies running on the target.");
      }
    };

    Blockly.Blocks['action_regex_filter'] = {
      init: function() {
        this.appendDummyInput()
            .appendField("🎯 Regex Pattern:")
            .appendField(new Blockly.FieldTextInput("[0-9]{1,3}\\\\.[0-9]{1,3}"), "PATTERN");
        this.appendValueInput("NAME").setCheck("String").appendField("   Input Text:");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null);
        this.setColour(290);
        this.setTooltip("Extracts matches from text using a regular expression.");
      }
    };
"""

# ── Python generators (JS) ───────────────────────────────────
PYTHON_GENERATORS_JS = """
    Blockly.Python['action_dns_resolve'] = function(block) {
        var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
        return 'run_scan(target=' + val + ', mode="dns")\\n';
    };

    Blockly.Python['action_ip_geolocation'] = function(block) {
        var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
        return 'run_scan(target=' + val + ', mode="geo")\\n';
    };

    Blockly.Python['action_phone_tracker'] = function(block) {
        var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
        return 'run_scan(target=' + val + ', mode="phone")\\n';
    };

    Blockly.Python['action_whois_lookup'] = function(block) {
        var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
        return 'run_scan(target=' + val + ', mode="whois")\\n';
    };

    Blockly.Python['action_robots_sitemap'] = function(block) {
        var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
        return 'run_scan(target=' + val + ', mode="robots")\\n';
    };

    Blockly.Python['action_ssl_audit'] = function(block) {
        var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
        return 'run_scan(target=' + val + ', mode="ssl_audit")\\n';
    };

    Blockly.Python['action_shodan_lookup'] = function(block) {
        var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
        return 'run_scan(target=' + val + ', mode="shodan")\\n';
    };

    Blockly.Python['action_http_header_audit'] = function(block) {
        var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
        return 'run_scan(target=' + val + ', mode="header_audit")\\n';
    };

    Blockly.Python['action_service_enum'] = function(block) {
        var val = Blockly.Python.valueToCode(block, 'TARGET', Blockly.Python.ORDER_ATOMIC) || "''";
        return 'run_scan(target=' + val + ', mode="service_enum")\\n';
    };

    Blockly.Python['action_regex_filter'] = function(block) {
        var val = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC) || "''";
        var pattern = block.getFieldValue('PATTERN');
        return 'run_scan(target=' + val + ', mode="regex", structural="' + pattern + '")\\n';
    };
"""
