import socket
import json
import urllib.request
import urllib.parse
import random
import re
import time
import ssl

# Try loading phonenumbers for validation blocks if installed
try:
    import phonenumbers
    from phonenumbers import carrier, geocoder, timezone
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False

# ==========================================
# 1. CORE UTILITY FUNCTIONS (PASSIVE OSINT SUITE)
# ==========================================

def perform_dns_lookup(target: str) -> str:
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    clean_host = clean_host.replace("https://", "").replace("http://", "").split("/")[0]
    if not clean_host:
        return "❌ ERROR: Target host string is empty."
        
    try:
        ip_addr = socket.gethostbyname(clean_host)
        return f"📡 DNS Resolution successful for [{clean_host}]\n📍 Resolved IP Address: {ip_addr}"
    except Exception as e:
        return f"❌ DNS Lookup Failed for target '{clean_host}': {str(e)}"

def perform_ip_geolocation(target: str) -> str:
    clean_ip = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    # Basic check to see if it looks like a domain instead of an IP
    if any(c.isalpha() for c in clean_ip):
        try:
            clean_ip = socket.gethostbyname(clean_ip.replace("https://", "").replace("http://", "").split("/")[0])
        except Exception:
            pass
            
    try:
        url = f"https://ipapi.co/{clean_ip}/json/"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if "error" in data:
                return f"❌ Geolocation Provider Error: {data.get('reason', 'Unknown Reason')}"
            return (f"🌐 IP Geolocation Metadata Summary:\n"
                    f"   • IP: {data.get('ip')}\n"
                    f"   • City/Region: {data.get('city')}, {data.get('region')}\n"
                    f"   • Country: {data.get('country_name')} ({data.get('country_code')})\n"
                    f"   • ASN/Org: {data.get('org', 'N/A')}")
    except Exception as e:
        return f"❌ Passive Geolocation Request Failed: {str(e)}"

def perform_phone_tracking(target: str) -> str:
    if not PHONENUMBERS_AVAILABLE:
        return "❌ Module Missing: 'phonenumbers' dependency package is not installed on this server environment."
    try:
        clean_num = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
        parsed_num = phonenumbers.parse(clean_num, None)
        if not phonenumbers.is_valid_number(parsed_num):
            return "❌ Input Validation Error: Provided configuration format is not a valid international E.164 phone structure."
            
        region = geocoder.description_for_number(parsed_num, "en")
        operator = carrier.name_for_number(parsed_num, "en")
        zones = timezone.time_zones_for_number(parsed_num)
        return (f"📞 Telephony Metadata Analysis:\n"
                f"   • Parsed Format: {phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}\n"
                f"   • Registered Region: {region or 'Unknown'}\n"
                f"   • Carrier/Provider: {operator or 'Unknown'}\n"
                f"   • Timezone Mapping: {', '.join(zones)}")
    except Exception as e:
        return f"❌ Telephony Registry Lookup Exception: {str(e)}"

def parse_robots_txt(target: str) -> str:
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_host.startswith(('http://', 'https://')):
        clean_host = 'https://' + clean_host
    clean_host = clean_host.split("/")[0] + "//" + clean_host.split("/")[2]
    
    try:
        url = f"{clean_host}/robots.txt"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            content = response.read().decode('utf-8', errors='ignore')
            lines = content.split('\n')
            disallowed = [line.strip() for line in lines if line.lower().startswith('disallow:')]
            if not disallowed:
                return f"📄 Robots.txt parsed at {url}.\nℹ️ No explicitly Disallowed navigation rules found."
            return f"📄 Isolated Robots.txt Disallow Directives ({len(disallowed)}):\n" + "\n".join(f"   • {line}" for line in disallowed[:15])
    except Exception as e:
        return f"❌ Failed to parse robots.txt for target base: {str(e)}"

def run_scan(target: str, mode: str, structural_regex: str = "") -> str:
    if mode == "dns":
        return perform_dns_lookup(target)
    elif mode == "geo":
        return perform_ip_geolocation(target)
    elif mode == "phone":
        return perform_phone_tracking(target)
    elif mode == "robots":
        return parse_robots_txt(target)
    elif mode == "subdomain_parse":
        clean_text = str(target).strip()
        found_domains = re.findall(r'(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}', clean_text)
        if not found_domains:
            return "ℹ️ OSINT Parser: No valid domain configurations isolated in source block text."
        return f"📋 Isolated Domain Formats:\n" + "\n".join(f"   • {dom}" for dom in set(found_domains))
    elif mode == "tls_check":
        clean_host = str(target).replace("https://", "").replace("http://", "").split("/")[0].strip()
        try:
            context = ssl.create_default_context()
            with socket.create_connection((clean_host, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=clean_host) as ssock:
                    version = ssock.version()
                    cipher = ssock.cipher()
                    return f"🔒 TLS Handshake Telemetry:\n   • Version Enabled: {version}\n   • Negotiated Cipher: {cipher[0]} ({cipher[1]} bits)"
        except Exception as e:
            return f"❌ TLS Profile Evaluation Failure: {str(e)}"
    elif mode == "regex":
        clean_text = str(target).strip()
        if not structural_regex:
            return "❌ Regex Error: Structural string filter pattern is unassigned."
        try:
            matches = re.findall(structural_regex, clean_text)
            return f"📊 Custom Regex Extraction Output ({len(matches)} matches):\n" + "\n".join(f"   • {m}" for m in matches[:10])
        except Exception as e:
            return f"❌ Regex Parser Exception Error: {str(e)}"
    else:
        return f"❌ Mode Error: Unrecognized passive assessment type pipeline called: {mode}"


# ==========================================
# 2. BLOCK DEFINITIONS JAVASCRIPT LAYER
# ==========================================

BLOCK_DEFINITIONS_JS = """
    Blockly.Blocks['when_sequence_activated'] = {
      init: function() {
        this.appendDummyInput().appendField("🏁 ON SEQUENCE EXECUTION").appendField(new Blockly.FieldTextInput("Recon_Chain_01"), "SEQUENCE_ID");
        this.setNextStatement(true, null); this.setColour(20);
        this.setTooltip("The mandatory primary entrance point for initiating automated passive data execution workflows.");
      }
    };

    Blockly.Blocks['action_wait_task'] = {
      init: function() {
        this.appendDummyInput().appendField("⏱️ Pause Automation for").appendField(new Blockly.FieldTextInput("2"), "SECONDS").appendField("seconds");
        this.setPreviousStatement(true, null); this.setNextStatement(true, null); this.setColour(20);
        this.setTooltip("Halts the sequencing execution thread for a fixed duration value before continuing to subsequent steps.");
      }
    };

    Blockly.Blocks['custom_input_string'] = {
      init: function() {
        this.appendDummyInput().appendField("🔤 Data String:").appendField(new Blockly.FieldTextInput("example.com"), "RAW_TEXT");
        this.setOutput(true, "String"); this.setColour(160);
        this.setTooltip("Outputs an unmutated raw text alpha-numeric block component sequence directly to standard inputs.");
      }
    };

    Blockly.Blocks['global_phone_preset'] = {
      init: function() {
        this.appendDummyInput().appendField("📱 Tel Prefix:").appendField(new Blockly.FieldTextInput("+1"), "CC_PREFIX").appendField("Body:").appendField(new Blockly.FieldTextInput("5550199"), "PHONE_BODY");
        this.setOutput(true, "String"); this.setColour(160);
        this.setTooltip("Combines country dialing configurations alongside normal mobile digits into an international phone record string.");
      }
    };

    Blockly.Blocks['action_dns_resolve'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("📡 Resolve DNS Record Host");
        this.setOutput(true, "String"); this.setColour(210);
        this.setTooltip("Queries standard network nameservers passively to determine the current mapped IPv4 address destination.");
      }
    };

    Blockly.Blocks['action_ip_geolocation'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("🌐 Fetch IP Location Profile");
        this.setOutput(true, "String"); this.setColour(210);
        this.setTooltip("Queries public geolocation datasets to return city, province, country code, and owner properties.");
      }
    };

    Blockly.Blocks['action_phone_tracker'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("📞 Parse Telecom Carrier Registry");
        this.setOutput(true, "String"); this.setColour(210);
        this.setTooltip("Uses public parsing models to safely identify the regional carrier provider and active timezone of a telephone node.");
      }
    };

    Blockly.Blocks['action_robots_sitemap'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("📄 Extract Robots Disallows");
        this.setOutput(true, "String"); this.setColour(210);
        this.setTooltip("Scrapes public site directory rule structures to highlight hidden path listings webmasters explicitly request indexers to skip.");
      }
    };

    Blockly.Blocks['action_regex_filter'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("🔍 Scan Text with Pattern:").appendField(new Blockly.FieldTextInput("[0-9]+"), "PATTERN");
        this.setOutput(true, "String"); this.setColour(280);
        this.setTooltip("Applies standard custom Regular Expression operations across input blocks to extract matching arrays of criteria.");
      }
    };

    Blockly.Blocks['action_subdomain_extractor'] = {
      init: function() {
        this.appendValueInput("TARGET_TEXT").setCheck("String").appendField("✂️ Extract Subdomains From Text");
        this.setOutput(true, "String"); this.setColour(210);
        this.setTooltip("Parses unstructured text records to isolate and extract valid subdomain structures using regex pattern matching.");
      }
    };

    Blockly.Blocks['action_tls_cipher_checker'] = {
      init: function() {
        this.appendValueInput("TARGET_HOST").setCheck("String").appendField("🔒 Evaluate TLS Header/Cipher Support");
        this.setOutput(true, "String"); this.setColour(210);
        this.setTooltip("Checks a specified target host for passive visibility of modern cryptographic handshakes and cipher suite negotiation parameters.");
      }
    };
"""


# ==========================================
# 3. CUSTOM CODE GENERATION LAYER
# ==========================================

PYTHON_GENERATORS_JS = """
    Blockly.Python.forBlock['when_sequence_activated'] = function(block) { 
      return '# Sequence Active: ' + block.getFieldValue('SEQUENCE_ID') + '\\n'; 
    };
    
    Blockly.Python.forBlock['action_wait_task'] = function(block) { 
      return 'time.sleep(' + block.getFieldValue('SECONDS') + ')\\n'; 
    };
    
    Blockly.Python.forBlock['custom_input_string'] = function(block) { 
      return ["'" + block.getFieldValue('RAW_TEXT').replace(/'/g, "\\\\'") + "'", 0]; 
    };
    
    Blockly.Python.forBlock['global_phone_preset'] = function(block) { 
      var val = block.getFieldValue('CC_PREFIX') + block.getFieldValue('PHONE_BODY');
      return ["'" + val.replace(/'/g, "\\\\'") + "'", 0]; 
    };
    
    Blockly.Python.forBlock['action_dns_resolve'] = function(block) {
      var val = Blockly.Python.valueToCode(block, 'NAME', 0) || "''";
      return ['run_scan(target=' + val + ', mode="dns")', 0];
    };
    
    Blockly.Python.forBlock['action_ip_geolocation'] = function(block) {
      var val = Blockly.Python.valueToCode(block, 'NAME', 0) || "''";
      return ['run_scan(target=' + val + ', mode="geo")', 0];
    };
    
    Blockly.Python.forBlock['action_phone_tracker'] = function(block) {
      var val = Blockly.Python.valueToCode(block, 'NAME', 0) || "''";
      return ['run_scan(target=' + val + ', mode="phone")', 0];
    };
    
    Blockly.Python.forBlock['action_robots_sitemap'] = function(block) {
      var val = Blockly.Python.valueToCode(block, 'NAME', 0) || "''";
      return ['run_scan(target=' + val + ', mode="robots")', 0];
    };
    
    Blockly.Python.forBlock['action_regex_filter'] = function(block) {
      var val = Blockly.Python.valueToCode(block, 'NAME', 0) || "''";
      var pat = block.getFieldValue('PATTERN') || "";
      return ['run_scan(target=' + val + ', mode="regex", structural_regex="' + pat.replace(/"/g, '\\\\"') + '")', 0];
    };

    Blockly.Python.forBlock['action_subdomain_extractor'] = function(block) {
      var val = Blockly.Python.valueToCode(block, 'TARGET_TEXT', 0) || "''";
      return ['run_scan(target=' + val + ', mode="subdomain_parse")', 0];
    };

    Blockly.Python.forBlock['action_tls_cipher_checker'] = function(block) {
      var val = Blockly.Python.valueToCode(block, 'TARGET_HOST', 0) || "''";
      return ['run_scan(target=' + val + ', mode="tls_check")', 0];
    };
"""


# ==========================================
# 4. TOOLBOX CORE COMPONENT MARKS
# ==========================================

TOOLBOX_XML = """
<xml id="toolbox" style="display: none">
    <category name="🎮 Control Flow" colour="#A05A2C">
        <block type="when_sequence_activated"></block>
        <block type="action_wait_task"></block>
    </category>
    <category name="✏️ Core Inputs" colour="#A0A0A0">
        <block type="custom_input_string"></block>
        <block type="global_phone_preset"></block>
    </category>
    <category name="🔎 Passive Recon Suite" colour="#4A90E2">
        <block type="action_dns_resolve"></block>
        <block type="action_ip_geolocation"></block>
        <block type="action_phone_tracker"></block>
        <block type="action_robots_sitemap"></block>
        <block type="action_subdomain_extractor"></block>
        <block type="action_tls_cipher_checker"></block>
    </category>
    <category name="🧪 Text Parsing" colour="#8A2BE2">
        <block type="action_regex_filter"></block>
    </category>
</xml>
"""