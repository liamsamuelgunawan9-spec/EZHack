import os
import socket
import json
import urllib.request
import random
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. UTILITY FUNCTIONS (UNTOUCHED CORE)
# ==========================================

def perform_dns_lookup(target: str) -> str:
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_host:
        return "❌ ERROR: You didn't enter a website name!"
    try:
        ip_addr = socket.gethostbyname(clean_host)
        return f"🔍 [SERVER LOOK-UP] Website: {clean_host} -> IP: {ip_addr}"
    except Exception as e:
        return f"❌ ERROR: {str(e)}"

def perform_ip_geolocation(target: str) -> str:
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_host:
        return "❌ ERROR: Target missing!"
    try:
        lookup_ip = socket.gethostbyname(clean_host)
        api_url = f"http://ip-api.com/json/{lookup_ip}"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as stream:
            payload = json.loads(stream.read().decode())
        if payload.get("status") == "fail":
            return f"❌ API ERROR: {payload.get('message')}"
        return f"🗺️ [LOCATION] IP: {lookup_ip} | Country: {payload.get('country')} | City: {payload.get('city')}"
    except Exception as e:
        return f"💥 ERROR: {str(e)}"

# ==========================================
# 2. STREAMLIT INTERFACE
# ==========================================

st.set_page_config(page_title="Horizon Studio", layout="wide")

st.title("⚡ Horizon Core Toolroom")
st.caption("Visual Block Configuration Environment")

# Sidebar Manual Tool runner to bypass iframe connectivity issues entirely
with st.sidebar:
    st.header("🎯 Direct Query Panel")
    st.markdown("If the visual canvas is syncing with the browser frame sandbox, run queries directly below:")
    
    tool_choice = st.selectbox("Select Utility", ["🔍 Website DNS Lookup", "🗺️ IP Geolocation"])
    query_input = st.text_input("Target Input (e.g., google.com)", "example.com")
    
    if st.button("Run Utility", type="primary"):
        if "DNS" in tool_choice:
            st.code(perform_dns_lookup(query_input))
        else:
            st.code(perform_ip_geolocation(query_input))

# ==========================================
# 3. VISUAL CANVAS EMBED
# ==========================================
st.markdown("### 🗺️ Visual Workspace Workspace")

blockly_html_payload = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://unpkg.com/blockly/blockly.min.js"></script>
  <script src="https://unpkg.com/blockly/python_compressed.js"></script>
  <script src="https://unpkg.com/blockly/blocks_compressed.js"></script>
  <style>
    html, body { height: 100%; margin: 0; padding: 0; background-color: #0b0c10; font-family: monospace; color: #1fec79; }
    #workspaceWrapper { display: flex; flex-direction: column; height: 680px; padding: 5px; box-sizing: border-box; }
    #blocklyDiv { flex: 1; border: 2px solid #45a29e; border-radius: 6px; box-shadow: 0 0 15px rgba(69, 162, 158, 0.15); }
    #debugTerminal { 
      height: 180px; 
      background: #000000; 
      border: 2px solid #ff0055; 
      margin-top: 12px; 
      padding: 12px; 
      overflow-y: auto; 
      white-space: pre-wrap; 
      font-size: 12px;
      border-radius: 6px;
      box-shadow: 0 0 15px rgba(255, 0, 85, 0.1);
    }
  </style>
</head>
<body>

  <div id="workspaceWrapper">
    <div id="blocklyDiv"></div>
    <div id="debugTerminal">> Awaiting block placement events...</div>
  </div>

  <xml id="toolbox" style="display: none">
    <category name="🏁 Sequences" colour="0">
      <block type="when_sequence_activated"></block>
    </category>
    <category name="🌐 Inputs" colour="160">
      <block type="custom_input_string"></block>
      <block type="multi_target_list"></block>
    </category>
    <category name="🎯 Actions" colour="210">
      <block type="action_scan"></block>
      <block type="protocol_verify"></block>
    </category>
  </xml>

  <script>
    // --- Existing Blocks ---
    Blockly.Blocks['when_sequence_activated'] = {
      init: function() {
        this.appendDummyInput().appendField("🚀 Sequence Start");
        this.setNextStatement(true, null);
        this.setColour(0);
      }
    };

    Blockly.Blocks['custom_input_string'] = {
      init: function() {
        this.appendDummyInput()
            .appendField("Target:")
            .appendField(new Blockly.FieldTextInput("example.com"), "RAW_TEXT");
        this.setOutput(true, "String");
        this.setColour(160);
      }
    };

    // --- New Input Block ---
    Blockly.Blocks['multi_target_list'] = {
      init: function() {
        this.appendDummyInput()
            .appendField("Multi-Targets:")
            .appendField(new Blockly.FieldTextInput("target1.com, target2.com"), "TARGETS");
        this.setOutput(true, "String");
        this.setColour(160);
      }
    };

    Blockly.Blocks['action_scan'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("Scan Target:");
        this.appendDummyInput()
            .appendField("Action:")
            .appendField(new Blockly.FieldDropdown([
              ["🔍 DNS Lookup","dns"],
              ["🗺️ Geolocation","geoip"]
            ]), "SCANTYPE");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(210);
      }
    };

    // --- New Action Block ---
    Blockly.Blocks['protocol_verify'] = {
      init: function() {
        this.appendValueInput("TARGET").setCheck("String").appendField("Verify Target:");
        this.appendDummyInput()
            .appendField("Check Option:")
            .appendField(new Blockly.FieldDropdown([
              ["🔒 SSL/TLS Certificate","ssl"],
              ["🔌 Open Ports Scan","ports"]
            ]), "VERIFYTYPE");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(210);
      }
    };

    // --- Python Compilers ---
    Blockly.Python.forBlock['when_sequence_activated'] = function(block) { return '# Sequence Active\\n'; };
    Blockly.Python.forBlock['custom_input_string'] = function(block) { return ['"' + block.getFieldValue('RAW_TEXT') + '"', 0]; };
    Blockly.Python.forBlock['multi_target_list'] = function(block) { return ['"' + block.getFieldValue('TARGETS') + '"', 0]; };
    
    Blockly.Python.forBlock['action_scan'] = function(block) {
      var type = block.getFieldValue('SCANTYPE');
      var val = Blockly.Python.valueToCode(block, 'NAME', 0) || "''";
      return 'run_scan(target=' + val + ', mode="' + type + '")\\n';
    };

    Blockly.Python.forBlock['protocol_verify'] = function(block) {
      var type = block.getFieldValue('VERIFYTYPE');
      var val = Blockly.Python.valueToCode(block, 'TARGET', 0) || "''";
      return 'verify_protocol(target=' + val + ', verification_mode="' + type + '")\\n';
    };

    // Inject parameters
    var workspace = Blockly.inject('blocklyDiv', {
      toolbox: document.getElementById('toolbox'),
      grid: {spacing: 20, length: 3, colour: '#1f2833', snap: true},
      trashcan: true
    });

    var terminal = document.getElementById("debugTerminal");

    function renderDebugLogs() {
      var allBlocks = workspace.getAllBlocks(false);
      var textOutput = "⚙️ LIVE WORKSPACE PARSER MATRIX\\n-----------------------------------------\\n";
      textOutput += "• Active elements mapped on floor: " + allBlocks.length + "\\n\\n";
      
      var sequenceCount = 0;
      for (var i = 0; i < allBlocks.length; i++) {
        if (allBlocks[i].type === 'when_sequence_activated') {
          sequenceCount++;
          textOutput += "🏁 [Sequence Sequence Node #" + sequenceCount + "] Enabled -> [UUID: " + allBlocks[i].id + "]\\n";
          
          var nextBlock = allBlocks[i].getNextBlock();
          while(nextBlock) {
            textOutput += "   └── Connected Step: " + nextBlock.type;
            if(nextBlock.type === 'action_scan') {
              textOutput += " [Action Mode: " + nextBlock.getFieldValue('SCANTYPE').toUpperCase() + "]";
            } else if(nextBlock.type === 'protocol_verify') {
              textOutput += " [Verification Mode: " + nextBlock.getFieldValue('VERIFYTYPE').toUpperCase() + "]";
            }
            textOutput += "\\n";
            nextBlock = nextBlock.getNextBlock();
          }
        }
      }
      
      if(sequenceCount === 0) {
        textOutput += "⚠️ STATUS ALERT: Drag and drop a 'Sequence Start' block onto the workspace canvas floor to begin compilation.";
      } else {
        textOutput += "\\n🟢 PARSING INTEGRITY STATUS: PIPELINE CHANNELS HEALTHY";
      }
      
      terminal.innerText = textOutput;
    }

    // Capture every block event instantaneously
    workspace.addChangeListener(function(e) {
      if (e.type === Blockly.Events.BLOCK_CREATE || 
          e.type === Blockly.Events.BLOCK_MOVE || 
          e.type === Blockly.Events.BLOCK_CHANGE || 
          e.type === Blockly.Events.BLOCK_DELETE) {
        renderDebugLogs();
      }
    });

    // Run interval check to catch text typing changes
    setInterval(renderDebugLogs, 200);
  </script>
</body>
</html>
"""

components.html(blockly_html_payload, height=700, scrolling=False)