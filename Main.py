import os
import socket
import json
import urllib.request
import random
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. LIVE UTILITY INTERFACE BACKEND
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
# 2. APPLICATION LAYOUT ENGINE
# ==========================================

st.set_page_config(page_title="Horizon Studio", layout="wide")

st.title("⚡ Horizon Core Toolroom")
st.caption("Visual Block Configuration & Live Compiling Environment")

# Sidebar Direct Processing fallback mechanism
with st.sidebar:
    st.header("🎯 Direct Query Panel")
    st.markdown("Run manual queries directly to check runtime functions without using the canvas:")
    
    tool_choice = st.selectbox("Select Utility", ["🔍 Website DNS Lookup", "🗺️ IP Geolocation"])
    query_input = st.text_input("Target Input", "example.com")
    
    if st.button("Run Utility", type="primary"):
        if "DNS" in tool_choice:
            st.code(perform_dns_lookup(query_input))
        else:
            st.code(perform_ip_geolocation(query_input))

# ==========================================
# 3. UNIFIED STABLE SANDBOX WORKSPACE (DUAL CONSOLE)
# ==========================================
st.markdown("### 🗺️ Visual Production Workspace Floor")

blockly_html_payload = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://unpkg.com/blockly/blockly.min.js"></script>
  <script src="https://unpkg.com/blockly/python_compressed.js"></script>
  <script src="https://unpkg.com/blockly/blocks_compressed.js"></script>
  <style>
    html, body { 
      height: 100%; 
      margin: 0; 
      padding: 0; 
      background-color: #0b0c10; 
      font-family: monospace; 
      color: #1fec79; 
      overflow: hidden;
    }
    
    #workspaceContainer { 
      display: flex; 
      width: 100%; 
      height: 720px; 
      gap: 15px; 
      padding: 10px; 
      box-sizing: border-box;
    }
    
    /* Left Panel - Drag/Drop Canvas Arena */
    #canvasFrame { 
      flex: 1.2; 
      display: flex; 
      flex-direction: column; 
    }
    
    #blocklyDiv { 
      flex: 1; 
      border: 2px solid #1f2833; 
      border-radius: 6px; 
    }
    
    /* Right Panel - Monitoring & Code Verification Stack */
    #monitorFrame { 
      flex: 0.8; 
      display: flex; 
      flex-direction: column; 
      gap: 12px; 
    }
    
    .consoleBox { 
      flex: 1; 
      background: #000000; 
      border-radius: 6px; 
      padding: 12px; 
      overflow-y: auto; 
      white-space: pre-wrap; 
      font-size: 11px;
    }
    
    #compilerConsole { border: 2px solid #66fcf1; color: #66fcf1; }
    #debugTerminal { border: 2px solid #ff0055; color: #1fec79; }
    
    .panelLabel {
      font-weight: bold;
      font-size: 11px;
      margin-bottom: 4px;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    
    #compilerLabel { color: #66fcf1; }
    #debugLabel { color: #ff0055; }
  </style>
</head>
<body>

  <div id="workspaceContainer">
    <div id="canvasFrame">
      <div class="panelLabel" style="color: #45a29e;">🧩 Flow Designer Canvas</div>
      <div id="blocklyDiv"></div>
    </div>
    
    <div id="monitorFrame">
      <div>
        <div class="panelLabel" id="compilerLabel">⚙️ Live Script Compiler Runtime</div>
        <pre class="consoleBox" id="compilerConsole">> Compiling workspace source tree...</pre>
      </div>
      
      <div>
        <div class="panelLabel" id="debugLabel">🤖 Canvas Event Diagnostics &amp; Structure Trace</div>
        <pre class="consoleBox" id="debugTerminal">> Initializing runtime hook loggers...</pre>
      </div>
    </div>
  </div>

  <xml id="toolbox" style="display: none">
    <category name="🏁 Sequences" colour="0">
      <block type="when_sequence_activated"></block>
    </category>
    <category name="🌐 Inputs" colour="160">
      <block type="custom_input_string"></block>
    </category>
    <category name="🎯 Actions" colour="210">
      <block type="action_scan"></block>
    </category>
  </xml>

  <script>
    // --------------------------------------------------
    // A. CUSTOM COMPONENT CONSTRAINTS SETUP
    // --------------------------------------------------
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

    // --------------------------------------------------
    // B. TRANSLATION SYNTAX MAPPING CONSTRUCTS
    // --------------------------------------------------
    Blockly.Python.forBlock['when_sequence_activated'] = function(block) { 
      return '# [Sequence Root Context Enabled]\\n'; 
    };
    Blockly.Python.forBlock['custom_input_string'] = function(block) { 
      return ["'" + block.getFieldValue('RAW_TEXT') + "'", 0]; 
    };
    Blockly.Python.forBlock['action_scan'] = function(block) {
      var type = block.getFieldValue('SCANTYPE');
      var val = Blockly.Python.valueToCode(block, 'NAME', 0) || "''";
      return 'run_pipeline_scan(target=' + val + ', module_type="' + type + '")\\n';
    };

    // Inject layout properties safely into viewport frame
    var workspace = Blockly.inject('blocklyDiv', {
      toolbox: document.getElementById('toolbox'),
      grid: {spacing: 20, length: 3, colour: '#1f2833', snap: true},
      trashcan: true
    });

    // Default Pre-loaded Structure Sequence Configuration Placement
    var defaultXml = '<xml><block type="when_sequence_activated" x="30" y="30"><next><block type="action_scan"><field name="SCANTYPE">dns</field><value name="NAME"><block type="custom_input_string"><field name="RAW_TEXT">google.com</field></block></value></block></next></block></xml>';
    Blockly.Xml.domToWorkspace(Blockly.Xml.textToDom(defaultXml), workspace);

    var compilerBox = document.getElementById("compilerConsole");
    var diagnosticsTerminal = document.getElementById("debugTerminal");

    // --------------------------------------------------
    // C. SECURE DUAL CONSOLE LOG MONITOR HANDLERS
    // --------------------------------------------------
    function syncConsoleOutputs() {
      var allBlocks = workspace.getAllBlocks(false);
      
      // 1. UPDATE DYNAMIC COMPILER LOGIC BOX
      var codeCompilationText = "⚙️ GENERATED PYTHON RUNTIME TARGET CODE:\\n-----------------------------------------\\n";
      var activePathFound = false;
      
      for (var i = 0; i < allBlocks.length; i++) {
        if (allBlocks[i].type === 'when_sequence_activated') {
          activePathFound = true;
          codeCompilationText += "def pipeline_execution_chain():\\n    # Entry initialization point confirmed\\n";
          
          var traceNode = allBlocks[i].getNextBlock();
          while (traceNode) {
            var scriptBlockCode = Blockly.Python.blockToCode(traceNode);
            if (typeof scriptBlockCode === 'string') {
              codeCompilationText += "    " + scriptBlockCode;
            } else if (Array.isArray(scriptBlockCode)) {
              codeCompilationText += "    " + scriptBlockCode[0] + "\\n";
            }
            traceNode = traceNode.getNextBlock();
          }
        }
      }
      
      if (!activePathFound) {
        codeCompilationText += "# ⚠️ STAGE ERROR: Missing a valid 'Sequence Start' block node context on the field canvas.";
      }
      compilerBox.innerText = codeCompilationText;

      // 2. UPDATE SYSTEM LOG EVENT BLOCK DIAGNOSTICS
      var diagnosticLogText = "📊 CANVAS RUNTIME DIAGNOSTICS MATRIX:\\n---------------------------------------\\n";
      diagnosticLogText += "• Block footprint density on canvas: " + allBlocks.length + " modules\\n";
      
      var sequenceCount = 0;
      for (var j = 0; j < allBlocks.length; j++) {
        if (allBlocks[j].type === 'when_sequence_activated') {
          sequenceCount++;
          diagnosticLogText += "👉 Sequence Chain #" + sequenceCount + " Identified [ID Reference: " + allBlocks[j].id + "]\\n";
          
          var connectionIterator = allBlocks[j].getNextBlock();
          var stepCounter = 0;
          while (connectionIterator) {
            stepCounter++;
            diagnosticLogText += "   ├── Step " + stepCounter + ": " + connectionIterator.type;
            if (connectionIterator.type === 'action_scan') {
              diagnosticLogText += " [Mode configuration parameter: " + connectionIterator.getFieldValue('SCANTYPE').toUpperCase() + "]";
            }
            diagnosticLogText += "\\n";
            connectionIterator = connectionIterator.getNextBlock();
          }
          if (stepCounter === 0) {
            diagnosticLogText += "   └── ⚠️ Trace Warning: Sequence empty. Drop validation actions below start node.\\n";
          }
        }
      }
      
      if (sequenceCount === 0) {
        diagnosticLogText += "\\n❌ ERROR FRAME: Workspace sequence parsing suspended. Execution sequence requires a core start component block node connection.";
      } else {
        diagnosticLogText += "\\n🟢 DIAGNOSTICS PARSING STATUS: SYSTEM VALID CHANNELS HEALTHY.";
      }
      
      diagnosticsTerminal.innerText = diagnosticLogText;
    }

    // Capture precise, non-breaking canvas changes safely inside the event loop hooks
    workspace.addChangeListener(function(e) {
      if (e.type === Blockly.Events.BLOCK_CREATE || 
          e.type === Blockly.Events.BLOCK_MOVE || 
          e.type === Blockly.Events.BLOCK_CHANGE || 
          e.type === Blockly.Events.BLOCK_DELETE) {
        syncConsoleOutputs();
      }
    });

    // Scheduler fallback guarantees text inputs and canvas variables update seamlessly without blocking browser threads
    setInterval(syncConsoleOutputs, 200);
    setTimeout(syncConsoleOutputs, 300);
  </script>
</body>
</html>
"""

components.html(blockly_html_payload, height=740, scrolling=False)