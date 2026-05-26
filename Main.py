import streamlit as st
import streamlit.components.v1 as components

# Set standard page canvas parameters
st.set_page_config(page_title="Horizon Studio Core", layout="wide")

st.title("⚡ Horizon Core Toolroom")
st.caption("Visual Pipeline Engine Architecture")

# Render custom styling container definitions
st.markdown(
    """
    <style>
    .reportview-container .main .block-container{
        padding-top: 1rem;
    }
    code {
        color: #1fec79 !important;
        background-color: #0b0c10 !important;
    }
    </style>
    """,
    unsafe_allowed_html=True
)

# Initialize global layout state variables safely
if "translated_python_code" not in st.session_state:
    st.session_state["translated_python_code"] = "# Drag layout blocks onto the workspace canvas floor to generate logic paths..."

# ==========================================
# WINDOW MESSAGE CHANNEL RECEIVER
# ==========================================
# Streamlit components are isolated. To capture the live block outputs 
# without triggering address parameter or browser lock exceptions,
# we use standard HTML storage tracking or explicit state checks.
query_parameters = st.query_params
if "live_payload" in query_parameters:
    st.session_state["translated_python_code"] = query_parameters["live_payload"]

# Define Layout Column Matrices
action_panel_col, workspace_canvas_col = st.columns([4, 8])

with action_panel_col:
    st.markdown("### 📝 Code Translation Behind the Blocks")
    st.code(st.session_state["translated_python_code"], language="python")
    
    st.markdown("---")
    st.markdown("##### 🎯 Core Network Diagnostics Engine")
    st.caption("Individual core functions run here upon compiling visual sequences.")

with workspace_canvas_col:
    st.markdown("### 🗺️ Visual Workspace Floor")

    # Expanded raw layout payload definition
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
          flex-direction: column;
          height: 750px; /* Expanded workspace height assignment */
          padding: 5px;
          box-sizing: border-box;
        }
        #blocklyDiv { 
          flex: 1; 
          border: 2px solid #1f2833; 
          border-radius: 6px; 
        }
        #canvasDiagnostics { 
          height: 100px; 
          background: #000000; 
          border: 2px solid #66fcf1; 
          margin-top: 8px; 
          padding: 12px; 
          overflow-y: auto; 
          white-space: pre-wrap;
          font-size: 11px;
          box-shadow: 0 0 15px rgba(102, 252, 241, 0.1);
        }
      </style>
    </head>
    <body>

      <div id="workspaceContainer">
        <div id="blocklyDiv"></div>
        <div id="canvasDiagnostics">> Engine ready. Arrange layout blocks to run translation passes...</div>
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
        // Custom Blockly Architecture Blocks Initialization
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
                .appendField("Target Value:")
                .appendField(new Blockly.FieldTextInput("example.com"), "RAW_TEXT");
            this.setOutput(true, "String");
            this.setColour(160);
          }
        };

        Blockly.Blocks['action_scan'] = {
          init: function() {
            this.appendValueInput("NAME").setCheck("String").appendField("Input Parameter:");
            this.appendDummyInput()
                .appendField("Utility Scan:")
                .appendField(new Blockly.FieldDropdown([
                  ["🔍 Server DNS Lookup", "dns"],
                  ["🗺️ IP Geolocation Map", "geoip"]
                ]), "SCANTYPE");
            this.setPreviousStatement(true, null);
            this.setNextStatement(true, null);
            this.setColour(210);
          }
        };

        // Code Generation Mapping Definitions
        Blockly.Python.forBlock['when_sequence_activated'] = function(block) { 
          return '# --- Active Sequence Block Sequence Start ---\\n'; 
        };
        Blockly.Python.forBlock['custom_input_string'] = function(block) { 
          return ['"' + block.getFieldValue('RAW_TEXT') + '"', 0]; 
        };
        Blockly.Python.forBlock['action_scan'] = function(block) {
          var type = block.getFieldValue('SCANTYPE');
          var val = Blockly.Python.valueToCode(block, 'NAME', 0) || "''";
          return 'execute_network_analysis_scan(target=' + val + ', profile_mode="' + type + '")\\n';
        };

        // Inject the configured workspace schema logic
        var workspace = Blockly.inject('blocklyDiv', {
          toolbox: document.getElementById('toolbox'),
          grid: {spacing: 22, length: 4, colour: '#1f2833', snap: true},
          trashcan: true
        });

        var loggerConsole = document.getElementById("canvasDiagnostics");
        var baseLocationUrl = window.parent.location.href.split('?')[0];

        function processWorkspaceTranslationLoop() {
          var allBlocks = workspace.getAllBlocks(false);
          var generatedScript = "";
          var sequenceFlag = false;
          
          var technicalLogs = "⚙️ LOCAL CORE TRANSLATOR STATUS:\\n";
          technicalLogs += "Total Canvas Nodes Configured: " + allBlocks.length + "\\n";

          for (var i = 0; i < allBlocks.length; i++) {
            if (allBlocks[i].type === 'when_sequence_activated') {
              sequenceFlag = true;
              generatedScript += Blockly.Python.blockToCode(allBlocks[i]);
              
              var pointer = allBlocks[i].getNextBlock();
              while(pointer) {
                var chunk = Blockly.Python.blockToCode(pointer);
                if (typeof chunk === 'string') {
                  generatedScript += chunk;
                } else if (Array.isArray(chunk)) {
                  generatedScript += chunk[0];
                }
                pointer = pointer.getNextBlock();
              }
            }
          }

          if (!sequenceFlag) {
            generatedScript = "# ⚠️ Visual canvas layout requires a Sequence Start block to generate logic paths.";
            technicalLogs += "⚠️ WARNING: A 'Sequence Start' header block is missing from the workspace canvas.";
          } else {
            technicalLogs += "🟢 Compilation successful. Pipeline strings serialized.";
          }

          loggerConsole.innerText = technicalLogs;

          // Native window synchronization interface to handle side-by-side rendering state updates
          try {
            var urlParams = new URLSearchParams(window.parent.location.search);
            if (urlParams.get("live_payload") !== generatedScript) {
              urlParams.set("live_payload", generatedScript);
              window.parent.history.replaceState({}, "", baseLocationUrl + "?" + urlParams.toString());
            }
          } catch(crossOriginException) {
            // Fallback warning handling in restrictive runtime environments
            loggerConsole.innerText += "\\n[Cross-Origin Layer Bound Detected: Syncing internally]";
          }
        }

        // Bind compiler hooks onto the drag-and-drop workspace triggers
        workspace.addChangeListener(function(event) {
          if (event.type === Blockly.Events.BLOCK_CREATE || 
              event.type === Blockly.Events.BLOCK_MOVE || 
              event.type === Blockly.Events.BLOCK_CHANGE || 
              event.type === Blockly.Events.BLOCK_DELETE) {
            processWorkspaceTranslationLoop();
          }
        });

        // Run system validation loops to capture asynchronous changes
        setInterval(processWorkspaceTranslationLoop, 300);
      </script>
    </body>
    </html>
    """

    # Embed visual studio floor with optimized height configuration parameters
    components.html(blockly_html_payload, height=780, scrolling=False)