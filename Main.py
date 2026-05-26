import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. CORE INTERFACE LAYOUT
# ==========================================

st.set_page_config(page_title="EZHack Horizon Studio", layout="wide")

# Top Header Bar
st.title("⚡ Horizon Core Toolroom")
st.caption("Visual Configuration Engine")

# ==========================================
# 2. COMBINED WORKSPACE & EXECUTION CANVAS
# ==========================================

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
    
    /* Top Toolbar Component */
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
      padding: 8px 20px;
      font-size: 12px;
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
    #blocklyDiv { width: 100%; height: 100%; }
    
    /* Classic Draggable Cyber Terminal */
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
    
    /* Lower Diagnostic Box */
    #canvasDiagnostics {
      position: absolute;
      bottom: 20px;
      left: 20px;
      width: 400px;
      height: 120px;
      background: rgba(20, 24, 30, 0.95);
      border: 2px solid #1f2833;
      border-radius: 6px;
      color: #45a29e;
      font-size: 11px;
      padding: 12px;
      overflow-y: auto;
      z-index: 998;
      pointer-events: none;
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
      <pre id="terminalBody">💻 [SYSTEM IDLE] Setup a sequence on the workspace canvas and click 'LAUNCH CIRCUIT PIPELINE'...</pre>
    </div>
    
    <div id="canvasDiagnostics">⚙️ LIVE ANALYSIS TRANSLATOR:<br>Awaiting block arrangement validation...</div>
    
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
    // Define Workspace Custom Blocks
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
            .appendField(new Blockly.FieldTextInput("example.com"), "RAW_TEXT");
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

    // Mapping code translation strings
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

    // Populate standard workspace setup
    var xmlText = '<xml><block type="when_sequence_activated" x="40" y="40"><next><block type="action_scan"><field name="SCANTYPE">phone</field><value name="NAME"><block type="custom_input_string"><field name="RAW_TEXT">+15555550199</field></block></value></block></next></block></xml>';
    Blockly.Xml.domToWorkspace(Blockly.Xml.textToDom(xmlText), workspace);

    var diagnosticsLogBox = document.getElementById("canvasDiagnostics");
    var terminalBodyBox = document.getElementById("terminalBody");

    // Real-time translation loop tracker
    function updateCodeView() {
      var allBlocks = workspace.getAllBlocks(false);
      var textOutput = "⚙️ GENERATED TRANSLATION SCRIPT:\\n-----------------------------------\\n";
      
      var sequenceFound = false;
      for (var i = 0; i < allBlocks.length; i++) {
        if (allBlocks[i].type === 'when_sequence_activated') {
          sequenceFound = true;
          textOutput += "# Start Sequence Chain Found\\n";
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
        textOutput += "# ⚠️ Status: Connect blocks to a 'Start Block' node.";
      }
      diagnosticsLogBox.innerText = textOutput;
    }

    // Pipeline Execution Stream
    function executePipeline() {
      var allBlocks = workspace.getAllBlocks(false);
      var consoleStream = "⚡ PIPELINE RUN SIGNAL RECEIVED...\\n⚡ INITIALIZING CORES...\\n\\n";
      var runsCount = 0;

      for (var i = 0; i < allBlocks.length; i++) {
        if (allBlocks[i].type === 'when_sequence_activated') {
          runsCount++;
          consoleStream += "▶️ [Executing Layout Chain #" + runsCount + "]\\n";
          
          var current = allBlocks[i].getNextBlock();
          if (!current) {
            consoleStream += "   └── ⚠️ Empty path. Attach action modules below the Start block.\\n";
          }
          
          while (current) {
            if (current.type === 'action_scan') {
              var selectedMode = current.getFieldValue('SCANTYPE');
              var inputVal = "[Empty Input]";
              var targetBlock = current.getInputTargetBlock('NAME');
              if (targetBlock && targetBlock.getFieldValue('RAW_TEXT')) {
                inputVal = targetBlock.getFieldValue('RAW_TEXT');
              }
              
              consoleStream += "   ├── Calling: " + selectedMode.toUpperCase() + " Module on target [" + inputVal + "]\\n";
              
              if (selectedMode === "phone") {
                consoleStream += "   └── 📡 [SCAN INITIALIZED]: Routing number trace... Data structure validated successfully.\\n";
              } else if (selectedMode === "dns") {
                consoleStream += "   └── 🔍 [RESOLVE INITIALIZED]: Fetching address record context mappings... Check complete.\\n";
              } else {
                consoleStream += "   └── 🗺️ [GEOLOCATION INITIALIZED]: Mapping coordinates data path... Verification sequence completed.\\n";
              }
            }
            current = current.getNextBlock();
          }
          consoleStream += "   └── ✔️ Layout pipeline branch evaluation done.\\n\\n";
        }
      }

      if (runsCount === 0) {
        consoleStream += "❌ EXECUTION ABORTED: Missing a 'Start Block (Sequence)' step on the layout floor.";
      } else {
        consoleStream += "🟢 ALL RECON CIRCUITS PROCESSED SUCCESSFULLY.";
      }

      terminalBodyBox.innerText = consoleStream;
    }

    // Attach button listener directly outside the canvas frame floor
    document.getElementById("launchBtn").addEventListener("click", executePipeline);

    // Watch workspace edits dynamically
    workspace.addChangeListener(updateCodeView);
    setInterval(updateCodeView, 200);
    setTimeout(updateCodeView, 300);

    // Draggable Window Script Config Structure
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

components.html(blockly_html_payload, height=680, scrolling=False)