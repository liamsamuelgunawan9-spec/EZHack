import os
import json
import streamlit as st
import streamlit.components.v1 as components
import io
from contextlib import redirect_stdout

# Pipeline Runtime Routing Initialization
if "terminal_history_output" not in st.session_state:
    st.session_state["terminal_history_output"] = "🚀 Automation Core Standby. Construct a block structure execution map..."

if "synced_workspace_code" not in st.session_state:
    st.session_state["synced_workspace_code"] = ""
    
if "blockly_xml_state" not in st.session_state:
    st.session_state["blockly_xml_state"] = ""

# Import non-core features and engine scripts securely
import Function

# ==========================================
# STREAMLIT FRAMEWORK MATRIX LAYER
# ==========================================

st.set_page_config(page_title="Horizon OSINT Workspace", layout="wide")

st.title("🛰️ Horizon Passive Intelligence Core")
st.caption("Industrial Scale Open-Source Reconnaissance Suite — 100% Free / Non-Intrusive")

st.markdown("### 🗺️ System Automation Floor Canvas (Ultra-Wide Viewport)")

# Create the custom component directory and index file dynamically on boot
COMPONENT_DIR = "blockly_component"
os.makedirs(COMPONENT_DIR, exist_ok=True)

component_html_content = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://unpkg.com/blockly/blockly.min.js"></script>
  <script src="https://unpkg.com/blockly/python_compressed.js"></script>
  <script src="https://unpkg.com/blockly/blocks_compressed.js"></script>
  <style>
    html, body { height: 100%; margin: 0; padding: 0; background-color: #0b0c10; font-family: monospace; color: #1fec79; overflow: hidden; }
    #workspaceWrapper { display: flex; flex-direction: column; height: 880px; padding: 5px; box-sizing: border-box; position: relative; }
    #blocklyDiv { flex: 1; border: 2px solid #45a29e; border-radius: 6px; position: relative; }
    
    #integratedTerminalBlock {
      position: absolute; top: 150px; left: 450px; width: 520px; background-color: #1f2833; border: 2px solid #1fec79; border-radius: 8px; z-index: 99; box-shadow: 0 10px 30px rgba(0,0,0,0.8);
    }
    #terminalHeader { padding: 8px 12px; cursor: move; background-color: #0b0c10; border-bottom: 2px solid #1fec79; font-weight: bold; color: #1fec79; display: flex; justify-content: space-between; font-size: 11px; align-items: center; }
    .termBody { padding: 12px; background-color: #000000; color: #ffffff; height: 340px; overflow-y: auto; font-size: 11px; white-space: pre-wrap; font-family: monospace; line-height: 1.4; }
    .windowCtrlBtn { background: #0b0c10; color: #ff0055; border: 1px solid #ff0055; padding: 2px 6px; cursor: pointer; border-radius: 4px; font-size: 10px; font-weight: bold; }
    .windowCtrlBtn:hover { background: #ff0055; color: #ffffff; }
  </style>
</head>
<body>

  <div id="workspaceWrapper">
    <div id="blocklyDiv"></div>
    
    <div id="integratedTerminalBlock">
      <div id="terminalHeader">
        <span id="headerLabelTitle">📺 MONITOR TERMINAL FEED</span>
        <button id="stateToggleActionBtn" class="windowCtrlBtn" onclick="toggleLocalTerminalState()">[-] MINIMIZE</button>
      </div>
      <div class="termBody" id="localTerminalContentText"></div>
    </div>
  </div>

  <xml id="toolbox" style="display: none">
    <category name="🏁 Sequence Triggers" colour="0">
      <block type="when_sequence_activated"></block>
    </category>
    <category name="🌐 Core Inputs" colour="160">
      <block type="custom_input_string"></block>
      <block type="global_phone_preset"></block>
      <block type="custom_phone_signature"></block>
    </category>
    <category name="📡 Network Channels" colour="210">
      <block type="action_scan_base"></block>
      <block type="action_dns_extractor"></block>
      <block type="action_http_header_audit"></block>
      <block type="action_subdomain_ct_logs"></block>
      <block type="action_threat_intel_reputation"></block>
    </category>
  </xml>

  <script>
    let workspaceInitialized = false;
    let workspace = null;

    // Listen for incoming pipeline parameters from the Streamlit frame
    function onStreamlitMessage(event) {
      if (event.data.type === "streamlit:render") {
        const args = event.data.args;
        
        // Dynamically update console text contents without destroying canvas state
        document.getElementById("localTerminalContentText").textContent = args.terminal_output;
        
        if (!workspaceInitialized) {
          // Safely execute external block definitions
          if (args.injects) {
            try { eval(args.injects); } catch (e) { console.error("Injection error:", e); }
          }

          // Inject Blockly Canvas
          workspace = Blockly.inject('blocklyDiv', {
            toolbox: document.getElementById('toolbox'),
            grid: { spacing: 25, length: 3, colour: '#1f2833', snap: true }, 
            trashcan: true
          });

          // Restore workspace blocks
          try {
            if (args.xml_state && args.xml_state.trim() !== "") {
              var dom = Blockly.utils.xml.textToDom(args.xml_state);
              Blockly.Xml.domToWorkspace(dom, workspace);
            }
          } catch (err) {
            console.error("Hydration Layer Failure:", err);
          }

          // Fire compilation updates safely to the parent process on changes
          workspace.addChangeListener(function(e) {
            if (e.type === Blockly.Events.BLOCK_CREATE || e.type === Blockly.Events.BLOCK_MOVE || 
                e.type === Blockly.Events.BLOCK_CHANGE || e.type === Blockly.Events.BLOCK_DELETE) {
              processLiveDebugCompilations();
            }
          });

          workspaceInitialized = true;
        }
      }
    }

    function processLiveDebugCompilations() {
      if (!workspace) return;
      var allBlocks = workspace.getAllBlocks(false);
      var generatedPythonCode = "";
      var sequenceFound = false;
      
      for (var i = 0; i < allBlocks.length; i++) {
        if (allBlocks[i].type === 'when_sequence_activated') {
          sequenceFound = true;
          generatedPythonCode += Blockly.Python.blockToCode(allBlocks[i]);
          var nextBlock = allBlocks[i].getNextBlock();
          while(nextBlock) {
            generatedPythonCode += Blockly.Python.blockToCode(nextBlock);
            nextBlock = nextBlock.getNextBlock();
          }
        }
      }
      
      var xmlDom = Blockly.Xml.workspaceToDom(workspace);
      var currentXmlText = Blockly.Xml.domToText(xmlDom);
      
      // FIXED: Bidirectional frame message sends payload directly back into Streamlit state
      window.parent.postMessage({
        setComponentValue: true,
        value: {
          code: generatedPythonCode,
          xml: currentXmlText
        }
      }, "*");
    }

    window.addEventListener("message", onStreamlitMessage);
    window.parent.postMessage({isStreamlitReady: true}, "*");

    // UI Window Mechanics
    var isTerminalMinimized = false;
    function toggleLocalTerminalState() {
      var tBody = document.getElementById("localTerminalContentText");
      var btn = document.getElementById("stateToggleActionBtn");
      var title = document.getElementById("headerLabelTitle");
      
      if(!isTerminalMinimized) {
        tBody.style.display = "none";
        btn.innerText = "[+] UNMINIMIZE";
        title.innerText = "📺 TERM (MINIMIZED)";
        isTerminalMinimized = true;
      } else {
        tBody.style.display = "block";
        btn.innerText = "[-] MINIMIZE";
        title.innerText = "📺 MONITOR TERMINAL FEED";
        isTerminalMinimized = false;
      }
    }

    var termWindow = document.getElementById('integratedTerminalBlock');
    var currentTermX = 450; var currentTermY = 150;
    var isDraggingWindow = false; var startX, startY;

    document.getElementById("terminalHeader").onmousedown = function(e) {
      if(e.target.className === "windowCtrlBtn") return;
      isDraggingWindow = true;
      startX = e.clientX - currentTermX;
      startY = e.clientY - currentTermY;
      e.preventDefault();
    };

    document.onmousemove = function(e) {
      if (!isDraggingWindow) return;
      currentTermX = e.clientX - startX;
      currentTermY = e.clientY - startY;
      termWindow.style.left = currentTermX + 'px';
      termWindow.style.top = currentTermY + 'px';
    };

    document.onmouseup = function() { isDraggingWindow = false; };
  </script>
</body>
</html>
"""

with open(os.path.join(COMPONENT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(component_html_content)

# Instantiate the registered component interface channel
blockly_component = components.declare_component("blockly_component", path=COMPONENT_DIR)

# Fire component view layer and parse returning values back into memory arrays
comp_res = blockly_component(
    xml_state=st.session_state["blockly_xml_state"],
    terminal_output=st.session_state["terminal_history_output"],
    injects=Function.BLOCKLY_INJECTS,
    key="horizon_blockly",
    height=900
)

# Assign harvested code blocks parameters directly to session state
if comp_res is not None:
    st.session_state["synced_workspace_code"] = comp_res.get("code", "")
    st.session_state["blockly_xml_state"] = comp_res.get("xml", "")

# Lower Utility Controls Zone
st.markdown("---")
st.markdown("### 🖥️ Main Engine Pipeline Terminal")

with st.expander("📋 View Compiled Execution Code Output Stream", expanded=False):
    st.text_area(
        "Live Track Payload Manifest", 
        value=st.session_state["synced_workspace_code"], 
        height=150,
        disabled=True
    )

if st.button("⚡ Run Block Automation Flow", type="primary", use_container_width=True):
    code_to_run = st.session_state["synced_workspace_code"].strip()
    
    if not code_to_run:
        st.error("❌ Pipeline Error: Drag and chain tools directly underneath the 'Sequence Start' trigger block first!")
    else:
        base_log_header = "🛰️ STREAMING PASSED ASSET DATA SECTIONS...\n-----------------------------------------\n"
        stdout_buffer = io.StringIO()
        
        try:
            exec_scope = {"run_scan": Function.run_scan}
            # Capture console print() commands executed within Function scripts
            with redirect_stdout(stdout_buffer):
                exec(code_to_run, exec_scope)
            
            st.session_state["terminal_history_output"] = base_log_header + stdout_buffer.getvalue()
            st.success("🟢 Execution automation run complete! Check terminal view log contents.")
            st.rerun()
            
        except Exception as runtime_err:
            st.session_state["terminal_history_output"] = base_log_header + stdout_buffer.getvalue() + f"\n💥 PIPELINE BREAK: {str(runtime_err)}"
            st.error(f"💥 PIPELINE BREAK: {str(runtime_err)}")