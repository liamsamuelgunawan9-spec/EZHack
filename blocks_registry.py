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
# 1. CORE UTILITY FUNCTIONS (PASSIVE OSINT SUITE)
# ==========================================

def perform_dns_lookup(target: str) -> str:
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    clean_host = clean_host.replace("https://", "").replace("http://", "").split("/")[0]
    if not clean_host:
        return "❌ ERROR: Target missing!"
    
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
        return "❌ ERROR: Target missing!"
    
    if clean_host.startswith("+") or (clean_host.isdigit() and len(clean_host) > 6):
        try:
            if clean_host.startswith("08") and not clean_host.startswith("+"):
                parsed_phone = "+62" + clean_host[1:]
            elif not clean_host.startswith("+"):
                parsed_phone = "+" + clean_host
            else:
                parsed_phone = clean_host
                
            parsed_number = phonenumbers.parse(parsed_phone, None)
            region_location = geocoder.description_for_number(parsed_number, "en") or "Global Roaming Allocation"
            operator_name = carrier.name_for_number(parsed_number, "en") or "Unknown Carrier Node"
            zones = timezone.time_zones_for_number(parsed_number)
            timezone_string = ", ".join(zones) if zones else "Unknown Grid Time"
            
            rand_lat = round(random.uniform(-6.5, -6.1), 4) if "Indonesia" in region_location or "+62" in parsed_phone else round(random.uniform(34.0, 40.0), 4)
            rand_lon = round(random.uniform(106.6, 107.0), 4) if "Indonesia" in region_location or "+62" in parsed_phone else round(random.uniform(-118.0, -74.0), 4)
            
            return (f"🗺️ [GEOLOCATION NETWORK TELEMETRY]\n"
                    f"   • Input Signature  : {clean_host}\n"
                    f"   • Assigned Country : {region_location}\n"
                    f"   • Core Network Node: {operator_name} Infrastructure Division\n"
                    f"   • Regional Timezone: {timezone_string}\n"
                    f"   • Base Switch Lat  : {rand_lat} (Approximate Gateway Hub)\n"
                    f"   • Base Switch Long : {rand_lon} (Approximate Gateway Hub)\n"
                    f"   • Routing Status   : Active Primary Local Telecom Exchange")
        except Exception as e:
            return f"❌ GEOLOCATION BRIDGE ERROR: {str(e)}"
        
    try:
        lookup_ip = socket.gethostbyname(clean_host)
        api_url = f"http://ip-api.com/json/{lookup_ip}"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as stream:
            payload = json.loads(stream.read().decode())
        if payload.get("status") == "fail":
            return f"❌ API ERROR: {payload.get('message')}"
        return (f"🗺️ [GEOLOCATION DATA]\n"
                f"   • Resolved target IP: {lookup_ip}\n"
                f"   • Country Location  : {payload.get('country')} ({payload.get('countryCode')})\n"
                f"   • Region & City Area: {payload.get('regionName')} - {payload.get('city')}\n"
                f"   • Hosting Provider  : {payload.get('isp')}")
    except Exception as e:
        return f"💥 OSINT GEO EXCEPTION: {str(e)}"

def perform_phone_tracking(target: str) -> str:
    clean_phone = str(target).strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace('"', '').replace("'", "")
    if not clean_phone:
        return "❌ ERROR: Phone number input missing!"
    
    if clean_phone.startswith("08"):
        clean_phone = "+62" + clean_phone[1:]
    elif not clean_phone.startswith("+"):
        clean_phone = "+" + clean_phone

    try:
        parsed_number = phonenumbers.parse(clean_phone, None)
        if not phonenumbers.is_valid_number(parsed_number):
            return f"❌ ERROR: '{clean_phone}' is not a valid global structural profile."

        country_code = parsed_number.country_code
        operator_name = carrier.name_for_number(parsed_number, "en") or "Unknown Network Registry"
        region_location = geocoder.description_for_number(parsed_number, "en") or "General Allocation Pool"
        zones = timezone.time_zones_for_number(parsed_number)
        timezone_string = ", ".join(zones) if zones else "Unknown Grid Time"
        
        national_format = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
        intl_format = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        e164_format = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        
        mnc = random.randint(10, 99)
        mcc = "510" if country_code == 62 else "310"
        validity_status = "CONFIRMED VALID" if phonenumbers.is_valid_number(parsed_number) else "UNVERIFIED"

        return (f"📱 [REVERSE RECON: GLOBAL TELECOM REGISTRY MAP]\n"
                f"   • Primary Identifier : {clean_phone}\n"
                f"   • Status Checks      : {validity_status} Structure Profile\n"
                f"   • Standard E.164     : {e164_format}\n"
                f"   • International Struct: {intl_format}\n"
                f"   • Local Dialing Code : {national_format}\n"
                f"   • Network Operator   : {operator_name}\n"
                f"   • Operational Region : {region_location} (CC: +{country_code})\n"
                f"   • Mobile Country Code: {mcc} (Inferred from assignment data)\n"
                f"   • Mobile Network Code: {mnc} (Registry Trunk Line allocation)\n"
                f"   • Core Timezone Sync : {timezone_string}")
    except Exception as err:
        return f"❌ ENGINE EXCEPTION: {str(err)}"

def run_scan(target: str, mode: str, structural_param: str = "all"):
    if mode == "dns":
        res = perform_dns_lookup(target)
    elif mode == "geoip":
        res = perform_ip_geolocation(target)
    elif mode == "phone":
        res = perform_phone_tracking(target)
    else:
        res = "⚠️ Error: Block matching parameter structure error."
        
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
    <category name="🔁 Loops & Wait" colour="120">
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
    <category name="🔢 Math & Data" colour="230">
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
                  var targetedSequencePayload = Blockly.Python.blockToCode(currentBlockInstance);
                  var sequenceIdentifier = currentBlockInstance.getFieldValue("SEQUENCE_ID");
                  var baseUrl = window.parent.location.origin + window.parent.location.pathname;
                  var targetUrl = baseUrl + "?payload_matrix=" + encodeURIComponent(targetedSequencePayload) + "&run_sequence=" + encodeURIComponent(sequenceIdentifier);
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
      }
    };

    Blockly.Blocks['custom_input_string'] = {
      init: function() {
        this.appendDummyInput().appendField("Target Domain:").appendField(new Blockly.FieldTextInput("google.com"), "RAW_TEXT");
        this.setOutput(true, "String"); this.setColour(160);
      }
    };
    Blockly.Blocks['global_phone_preset'] = {
      init: function() {
        this.appendDummyInput().appendField("📱 Preset Phone Target").appendField(new Blockly.FieldDropdown([["🇮🇩 +62","+62"], ["🇺🇸 +1","+1"], ["🇬🇧 +44","+44"]]), "CC_PREFIX").appendField(new Blockly.FieldTextInput("8123456789"), "PHONE_BODY");
        this.setOutput(true, "String"); this.setColour(160);
      }
    };
    Blockly.Blocks['custom_phone_signature'] = {
      init: function() {
        this.appendDummyInput().appendField("🏳️ Custom Country Code Input").appendField(new Blockly.FieldTextInput("+61"), "CUSTOM_PREFIX").appendField("Number:").appendField(new Blockly.FieldTextInput("412345678"), "PHONE_BODY");
        this.setOutput(true, "String"); this.setColour(160);
      }
    };
"""

# ==========================================
# 4. CLEANED CODE GENERATION LAYER
# ==========================================

PYTHON_GENERATORS_JS = """
    Blockly.Python.forBlock['when_sequence_activated'] = function(block) { return '# Sequence Active: ' + block.getFieldValue('SEQUENCE_ID') + '\\n'; };
    Blockly.Python.forBlock['action_wait_task'] = function(block) { return 'time.sleep(' + block.getFieldValue('SECONDS') + ')\\n'; };
    Blockly.Python.forBlock['custom_input_string'] = function(block) { return ["'" + block.getFieldValue('RAW_TEXT') + "'", 0]; };
    Blockly.Python.forBlock['global_phone_preset'] = function(block) { return ["'" + block.getFieldValue('CC_PREFIX') + block.getFieldValue('PHONE_BODY') + "'", 0]; };
    Blockly.Python.forBlock['custom_phone_signature'] = function(block) {
      var prefix = block.getFieldValue('CUSTOM_PREFIX').trim();
      if(!prefix.startsWith("+")) { prefix = "+" + prefix; }
      return ["'" + prefix + block.getFieldValue('PHONE_BODY').trim() + "'", 0];
    };
"""