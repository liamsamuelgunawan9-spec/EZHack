import os
import json
import random
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. CORE INTERFACE ARCHITECTURE
# ==========================================

st.set_page_config(page_title="EZHack Horizon Studio", layout="wide")

st.title("⚡ Horizon Core Toolroom")
st.caption("Multi-sequence layout compilation engine.")

# ==========================================
# 2. VISUAL CANVAS EMBED WITH FLOATING TERMINAL UI
# ==========================================
st.markdown("### 🗺️ Visual Studio Workspace Canvas")

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
      font-family: sans-serif; 
      overflow: hidden; 
    }
    #containerDiv { position: relative; width: 100%; height: 600px; }
    #blocklyDiv { width: 100%; height: 100%; border: 2px solid #1f2833; border-radius: 6px; }
    
    /* Draggable Terminal Styling Window */
    #draggableTerminal {
      position: absolute;
      top: 20px;
      right: 20px;
      width: 440px;
      height: 320px;
      z-index: 999;
      background: rgba(11, 12, 16, 0.96);
      border: 2px solid #66fcf1;
      border-radius: 8px;
      box-shadow: 0 0 25px rgba(102, 252, 241, 0.3);
      display: flex;
      flex-direction: column;
    }
    #terminalHeader {
      padding: 10px;
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
      padding: 12px;
      margin: 0;
      background: #0b0c10;
      color: #1fec79;
      font-family: monospace;
      font-size: 12px;
      overflow-y: auto;
      white-space: pre-wrap;
    }
    
    /* Internal Engine Status Box */
    #canvasDiagnostics {
      position: absolute;
      bottom: 15px;
      left: 15px;
      width: 390px;
      height: 140px;
      background: rgba(20, 24, 30, 0.95);
      border: 2px solid #1fec79;
      border-radius: 6px;
      color: #1fec79;
      font-family: monospace;
      font-size: 11px;
      padding: 12px;
      overflow-y: auto;
      z-index: 998;
      pointer-events: none;
      box-shadow: 0 0 15px rgba(31, 236, 121, 0.2);
    }
  </style>
</head>
<body>

  <div id="containerDiv">
    <div id="draggableTerminal">
      <div id="terminalHeader">🤖 LIVE MONITOR OUTPUT STREAM</div>
      <pre id="terminalBody">💻 [READY] Awaiting system pipeline generation execution signals...</pre>
    </div>
    
    <div id="canvasDiagnostics">⚙️ EVENT ENGINE SYSTEM LOGGER:<br>🟢 Core systems ready. Drop a layout block to execute tracking...</div>
    
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
    // Define Block Schematics Internals
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

    // Code compilation generator linkages
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

    // Populate the initial layout components
    var xmlText = '<xml><block type="when_sequence_activated" x="40" y="40"><next><block type="action_scan"><field name="SCANTYPE">phone</field><value name="NAME"><block type="custom_input_string"><field name="RAW_TEXT">+15555550199</field></block></value></block></next></block></xml>';
    Blockly.Xml.domToWorkspace(Blockly.Xml.textToDom(xmlText), workspace);

    var diagnosticsLogBox = document.getElementById("canvasDiagnostics");
    var terminalBodyBox = document.getElementById("terminalBody");

    // ⚡ INSTANT LIVE RE-COMPILER RUNTIME MATRIX
    function compileAndRenderLayout() {
      var allBlocks = workspace.getAllBlocks(false);
      var sequenceCount = 0;
      
      var loggerReport = "⚙️ ENGINE DIAGNOSTICS LOG:<br>✨ Total Blocks Active: " + allBlocks.length + "<br>";
      var virtualTerminalConsoleStream = "⚡ MONITOR STREAM ACTIVE...\\n⚡ EXECUTING ACTIVE SEQUENCE CHAINS:\\n\\n";

      for (var i = 0; i < allBlocks.length; i++) {
        if (allBlocks[i].type === 'when_sequence_activated') {
          sequenceCount++;
          loggerReport += "<span style='color:#66fcf1;'>🏁 Registered Sequence #" + sequenceCount + " (ID: " + allBlocks[i].id.substring(0,5) + ")</span><br>";
          virtualTerminalConsoleStream += "▶️ [Sequence #" + sequenceCount + " Started]\\n";
          
          var nextBlock = allBlocks[i].getNextBlock();
          var directSteps = 0;
          
          while (nextBlock) {
            directSteps++;
            if (nextBlock.type === 'action_scan') {
              var selectedMode = nextBlock.getFieldValue('SCANTYPE');
              // Extract text target value fields safely
              var targetInputStr = "[Empty Target Input]";
              var targetBlock = nextBlock.getInputTargetBlock('NAME');
              if (targetBlock && targetBlock.getFieldValue('RAW_TEXT')) {
                targetInputStr = targetBlock.getFieldValue('RAW_TEXT');
              }
              
              virtualTerminalConsoleStream += "   ├── Running: [" + selectedMode.toUpperCase() + "] Mode on target: " + targetInputStr + "\\n";
              
              // Localized simulation mock updates
              if (selectedMode === "phone") {
                virtualTerminalConsoleStream += "   └── 📡 [SCAN REPORT]: Target: " + targetInputStr + " | Location Code: US/CA | Active Circuit Verification: OK\\n";
              } else if (selectedMode === "dns") {
                virtualTerminalConsoleStream += "   └── 🔍 [SCAN REPORT]: Host resolve check performed on string target target successfully.\\n";
              } else {
                virtualTerminalConsoleStream += "   └── 🗺️ [SCAN REPORT]: Query parsed through provider routing blocks successfully.\\n";
              }
            }
            nextBlock = nextBlock.getNextBlock();
          }
          loggerReport += "   └── Connected chain path height: " + directSteps + " blocks.\\n";
          virtualTerminalConsoleStream += "   └── ✔️ Sequence sequence path processing finished.\\n\\n";
        }
      }

      if (sequenceCount === 0) {
        loggerReport += "<span style='color:#ff3366;'>⚠️ CRITICAL STATUS: Missing Sequence Start block!</span><br>";
        virtualTerminalConsoleStream += "⚠️ WARNING: Connect modules into an active Start Block component to run analytics processing loops.";
      }

      diagnosticsLogBox.innerHTML = loggerReport;
      terminalBodyBox.innerText = virtualTerminalConsoleStream;
    }

    // Assign change monitors for explicit canvas event trigger reactions
    workspace.addChangeListener(function(event) {
      if (event.type === Blockly.Events.BLOCK_CREATE || 
          event.type === Blockly.Events.BLOCK_MOVE || 
          event.type === Blockly.Events.BLOCK_CHANGE || 
          event.type === Blockly.Events.BLOCK_DELETE) {
        compileAndRenderLayout();
      }
    });

    // 0.1s heartbeat checking system loops to capture ongoing typing changes instantly
    setInterval(compileAndRenderLayout, 100);
    setTimeout(compileAndRenderLayout, 200);

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

components.html(blockly_html_payload, height=620, scrolling=False)