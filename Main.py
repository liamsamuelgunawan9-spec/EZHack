import os
import socket
import json
import urllib.request
import random
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. CORE INTERFACE LAYOUT & STYLING
# ==========================================

st.set_page_config(page_title="Horizon Studio Core", layout="wide")

# Injection of cyber dark aesthetic variables
st.markdown(
    """
    <style>
    .reportview-container .main .block-container {
        padding-top: 1rem;
    }
    body {
        background-color: #0b0c10;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("⚡ Horizon Core Toolroom")
st.caption("Visual Pipeline Engine Architecture")

# ==========================================
# 2. COMBINED WORKSPACE & LIVE PIPELINE CANVAS
# ==========================================
st.markdown("### 🗺️ Visual Workspace Floor")

blockly_html_payload = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Blockly Workspace</title>
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
      overflow: hidden; 
    }
    
    /* Top Toolbar Outside Grid Arena */
    #controlBar {
      height: 50px;
      background: #1f2833;
      border-bottom: 2px solid #45a29e;
      display: flex;
      align-items: center;
      padding-left: 20px;
    }
    
    #launchBtn {
      background: #1fec79;
      color: #0b0c10;
      border: none;
      padding: 8px 24px;
      font-size: 11px;
      font-weight: bold;
      border-radius: 4px;
      cursor: pointer;
      box-shadow: 0 0 10px rgba(31, 236, 121, 0.4);
      transition: all 0.2s ease;
    }
    
    #launchBtn:hover {
      background: #66fcf1;
      box-shadow: 0 0 15px rgba(102, 252, 241, 0.6);
    }

    #containerDiv { position: relative; width: 100%; height: calc(100% - 52px); }
    #blocklyDiv { width: 100%; height: 700px; }
    
    /* Classic Floating Draggable Terminal Screen */
    #draggableTerminal {
      position: absolute;
      top: 20px;
      right: 20px;
      width: 460px;
      height: 340px;
      z-index: 999;
      background: rgba(11, 12, 16, 0.96);
      border: 2px solid #66fcf1;
      border-radius: 8px;
      box-shadow: 0 0 25px rgba(102, 252, 241, 0.3);
      display: flex;
      flex-direction: column;
    }
    #terminalHeader {
      padding: 12px;
      cursor: move;
      background: #1f2833;
      border-bottom: 2px solid #45a29e;
      color: #66fcf1;
      font-weight: bold;
      font-size: 11px;
      user-select: none;
    }
    #terminalBody {
      flex: 1;
      padding: 15px;
      margin: 0;
      background: #0b0c10;
      color: #1fec79;
      font-size: 12px;
      overflow-y: auto;
      white-space: pre-wrap;
    }
    
    /* Lower Translation Output Logger Panel */
    #canvasDiagnostics {
      position: absolute;
      bottom: 40px;
      left: 20px;
      width: 440px;
      height: 180px;
      background: rgba(20, 24, 30, 0.95);
      border: 2px solid #1f2833;
      border-radius: 6px;
      color: #66fcf1;
      font-size: 11px;
      padding: 12px;
      overflow-y: auto;
      z-index: 998;
      pointer-events: none;
      box-shadow: 0 0 15px rgba(31, 236, 121, 0.1);
    }
  </style>
</head>
<body>

  <div id="controlBar">
    <button id="launchBtn">🚀 LAUNCH CIRCUIT PIPELINE</button>
  </div>

  <div id="containerDiv">
    <div id="draggableTerminal">
      <div id="terminalHeader">🤖 LIVE MONITOR OUTPUT STREAM</div>
      <pre id="terminalBody">💻 [SYSTEM IDLE] Connect elements inside a sequence chain and hit execution launch parameters...</pre>
    </div>
    
    <pre id="canvasDiagnostics">⚙️ LIVE SCRIPT COMPILER RUNTIME:</pre>
    
    <div id="blocklyDiv"></div>
  </div>

  <xml id="toolbox" style="display: none">
    <category name="🏁 Sequence Starts" colour="0">
      <block type="when_sequence_activated"></block>
    </category>
    <category name="🌐 Targets &amp; Inputs" colour="160">
      <block type="custom_input_string"></block>
    </category>
    <category name="🎯 Scanners &amp; Actions" colour="210">
      <block type="action_scan"></block>
    </category>
  </xml>

  <script>
    // Component Structural Custom Initialization
    Blockly.Blocks['when_sequence_activated'] = {
      init: function() {
        this.appendDummyInput().appendField("🚀 Start Block (Sequence)");
        this.setNextStatement(true, null);
        this.setColour(0);
      }
    };

    Blockly.Blocks['custom_input_string'] = {
      init: function() {
        this.appendDummyInput()
            .appendField("Type Target:")
            .appendField(new Blockly.FieldTextInput("+15555550199"), "RAW_TEXT");
        this.setOutput(true, "String");
        this.setColour(160);
      }
    };

    Blockly.Blocks['action_scan'] = {
      init: function() {
        this.appendValueInput("NAME").setCheck("String").appendField("Target info to check:");
        this.appendDummyInput()
            .appendField("Action:")
            .appendField(new Blockly.FieldDropdown([
              ["📱 Phone Number Scan", "phone"], 
              ["🔍 Website Server Look-up", "dns"],
              ["🗺️ IP Address Location", "geoip"]
            ]), "SCANTYPE");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(210);
      }
    };

    // Translation Code Engine Mappings
    Blockly.Python.forBlock['when_sequence_activated'] = function(block) { return '# [Start Sequence]\\n'; };
    Blockly.Python.forBlock['custom_input_string'] = function(block) { return ['"' + block.getFieldValue('RAW_TEXT') + '"', 0]; };
    Blockly.Python.forBlock['action_scan'] = function(block) {
      var type = block.getFieldValue('SCANTYPE');
      var val = Blockly.Python.valueToCode(block, 'NAME', 0) || "''";
      return 'run_utility_scan(' + val + ', "' + type + '")\\n';
    };

    var workspace = Blockly.inject('blocklyDiv', {
      toolbox: document.getElementById('toolbox'),
      grid: {spacing: 20, length: 3, colour: '#1f2833', snap: true},
      trashcan: true
    });

    // Default Starting Configuration Elements
    var xmlText = '<xml><block type="when_sequence_activated" x="40" y="40"><next><block type="action_scan"><field name="SCANTYPE">phone</field><value name="NAME"><block type="custom_input_string"><field name="RAW_TEXT">+15555550199</field></block></value></block></next></block></xml>';
    Blockly.Xml.domToWorkspace(Blockly.Xml.textToDom(xmlText), workspace);

    var diagnosticsLogBox = document.getElementById("canvasDiagnostics");
    var terminalBodyBox = document.getElementById("terminalBody");

    // Dynamic Live Code Compilation Updates
    function updateLiveTranslatedCode() {
      var allBlocks = workspace.getAllBlocks(false);
      var textOutput = "⚙️ LIVE TRANSLATED PYTHON CODE:\\n-----------------------------------\\n";
      
      var sequenceFound = false;
      for (var i = 0; i < allBlocks.length; i++) {
        if (allBlocks[i].type === 'when_sequence_activated') {
          sequenceFound = true;
          textOutput += "# Start Sequence Active Path\\n";
          var nextBlock = allBlocks[i].getNextBlock();
          while (nextBlock) {
            var blockCode = Blockly.Python.blockToCode(nextBlock);
            if (typeof blockCode === 'string') textOutput += blockCode;
            else if (Array.isArray(blockCode)) textOutput += blockCode[0] + "\\n";
            nextBlock = nextBlock.getNextBlock();
          }
        }
      }
      if (!sequenceFound) {
        textOutput += "# ⚠️ Status: Attach workspace modules to an active Start Block node.";
      }
      diagnosticsLogBox.innerText = textOutput;
    }

    // Interactive Action Emulation Output Channels
    function triggerPipelineProcessing() {
      var allBlocks = workspace.getAllBlocks(false);
      var streamLogs = "⚡ INITIALIZING PIPELINE DISPATCH SEQUENCE...\\n⚡ SYNCING RECON CORES...\\n\\n";
      var activeRuns = 0;

      for (var i = 0; i < allBlocks.length; i++) {
        if (allBlocks[i].type === 'when_sequence_activated') {
          activeRuns++;
          streamLogs += "▶️ [Processing Sequence Workspace Chain #" + activeRuns + "]\\n";
          
          var current = allBlocks[i].getNextBlock();
          if (!current) {
            streamLogs += "   └── ⚠️ Trace Empty. Drop scanner tools directly underneath the Start block node.\\n";
          }
          
          while (current) {
            if (current.type === 'action_scan') {
              var modeType = current.getFieldValue('SCANTYPE');
              var inputStr = "[Null Parameter]";
              var targetBlock = current.getInputTargetBlock('NAME');
              if (targetBlock && targetBlock.getFieldValue('RAW_TEXT')) {
                inputStr = targetBlock.getFieldValue('RAW_TEXT');
              }
              
              streamLogs += "   ├── Running: " + modeType.toUpperCase() + " Module checks against field input [" + inputStr + "]\\n";
              
              if (modeType === "phone") {
                streamLogs += "   └── 📡 [TELEPHONY SCAN COMPLETION]: Circuit trace mapped. Location properties verified via mock carrier registry nodes.\\n";
              } else if (modeType === "dns") {
                streamLogs += "   └── 🔍 [DNS RECORDS COMPLETION]: Domain resolved to host routing matrix structure records successfully.\\n";
              } else {
                streamLogs += "   └── 🗺️ [IP GEOLOCATION COMPLETION]: Geometric parameters assigned. Mapping parameters trace finalized successfully.\\n";
              }
            }
            current = current.getNextBlock();
          }
          streamLogs += "   └── ✔️ Workspace layout branch execution trace completed.\\n\\n";
        }
      }

      if (activeRuns === 0) {
        streamLogs += "❌ EXECUTION FATAL: Missing a 'Start Block (Sequence)' node element on the workspace canvas floor.";
      } else {
        streamLogs += "🟢 CORES PIPELINE SEQUENCE DISPATCH PROCESSED WITH NO ERRORS.";
      }

      terminalBodyBox.innerText = streamLogs;
    }

    // Attach button functionality to top-left bar outside canvas arena area
    document.getElementById("launchBtn").addEventListener("click", triggerPipelineProcessing);

    // Track real-time movement changes instantly
    workspace.addChangeListener(updateLiveTranslatedCode);
    setInterval(updateLiveTranslatedCode, 150);
    setTimeout(updateLiveTranslatedCode, 250);

    // Terminal Drag Setup Operations
    var windowFrame = document.getElementById("draggableTerminal");
    var topHeader = document.getElementById("terminalHeader");
    var isDragging = false;
    var cX, cY, iX, iY, xOff = 0, yOff = 0;

    topHeader.addEventListener("mousedown", function(e) {
      iX = e.clientX - xOff; iY = e.clientY - yOff;
      if (e.target === topHeader) isDragging = true;
    }, false);
    document.addEventListener("mouseup", function() { isDragging = false; }, false);
    document.addEventListener("mousemove", function(e) {
      if (isDragging) {
        e.preventDefault();
        cX = e.clientX - iX; cY = e.clientY - iY;
        xOff = cX; yOff = cY;
        windowFrame.style.transform = "translate3d(" + cX + "px, " + cY + "px, 0)";
      }
    }, false);
  </script>
</body>
</html>
"""

# Render the layout components safely inside the fixed component arena
components.html(blockly_html_payload, height=760, scrolling=False)