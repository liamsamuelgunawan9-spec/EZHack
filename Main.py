import os
import json
import urllib.parse
import streamlit as st
import streamlit.components.v1 as components

# Import non-core features and engine scripts securely
import Function

# Pipeline Runtime Routing Initialization
if "terminal_history_output" not in st.session_state:
    st.session_state["terminal_history_output"] = "🚀 Automation Core Standby. Construct a block structure execution map..."

# ==========================================
# STREAMLIT FRAMEWORK MATRIX LAYER
# ==========================================

st.set_page_config(page_title="Horizon OSINT Workspace", layout="wide")

st.title("🛰️ Horizon Passive Intelligence Core")
st.caption("Industrial Scale Open-Source Reconnaissance Suite — 100% Free / Non-Intrusive")

st.markdown("### 🗺️ System Automation Floor Canvas (Ultra-Wide Viewport)")

if "synced_workspace_code" not in st.session_state:
    st.session_state["synced_workspace_code"] = ""
    
if "blockly_xml_state" not in st.session_state:
    st.session_state["blockly_xml_state"] = ""

# Parse tracking inputs passed back via JavaScript URL updates
try:
    incoming_payload = st.query_params.get("payload_matrix", "")
    if incoming_payload:
        st.session_state["synced_workspace_code"] = urllib.parse.unquote(incoming_payload)
        
    incoming_xml = st.query_params.get("xml_matrix", "")
    if incoming_xml:
        st.session_state["blockly_xml_state"] = urllib.parse.unquote(incoming_xml)
except Exception:
    pass

# Safely serialize values to prevent JS runtime strings breakage
safe_xml_state = json.dumps(st.session_state.get("blockly_xml_state", ""))
safe_terminal_output = json.dumps(st.session_state.get("terminal_history_output", ""))

blockly_html_payload = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://unpkg.com/blockly/blockly.min.js"></script>
  <script src="https://unpkg.com/blockly/python_compressed.js"></script>
  <script src="https://unpkg.com/blockly/blocks_compressed.js"></script>
  <style>
    html, body {{ height: 100%; margin: 0; padding: 0; background-color: #0b0c10; font-family: monospace; color: #1fec79; overflow: hidden; }}
    #workspaceWrapper {{ display: flex; flex-direction: column; height: 880px; padding: 5px; box-sizing: border-box; position: relative; }}
    #blocklyDiv {{ flex: 1; border: 2px solid #45a29e; border-radius: 6px; position: relative; }}
    
    #integratedTerminalBlock {{
      position: absolute; top: 150px; left: 450px; width: 520px; background-color: #1f2833; border: 2px solid #1fec79; border-radius: 8px; z-index: 99; box-shadow: 0 10px 30px rgba(0,0,0,0.8);
    }}
    #terminalHeader {{ padding: 8px 12px; cursor: move; background-color: #0b0c10; border-bottom: 2px solid #1fec79; font-weight: bold; color: #1fec79; display: flex; justify-content: space-between; font-size: 11px; align-items: center; }}
    .termBody {{ padding: 12px; background-color: #000000; color: #ffffff; height: 340px; overflow-y: auto; font-size: 11px; white-space: pre-wrap; font-family: monospace; line-height: 1.4; }}
    .windowCtrlBtn {{ background: #0b0c10; color: #ff0055; border: 1px solid #ff0055; padding: 2px 6px; cursor: pointer; border-radius: 4px; font-size: 10px; font-weight: bold; }}
    .windowCtrlBtn:hover {{ background: #ff0055; color: #ffffff; }}
  </style>
</head>
<body>

  <div id="workspaceWrapper">
    <div id="blocklyDiv">
    
      <div id="integratedTerminalBlock">
        <div id="terminalHeader">
          <span id="headerLabelTitle">📺 MONITOR TERMINAL FEED</span>
          <button id="stateToggleActionBtn" class="windowCtrlBtn" onclick="toggleLocalTerminalState()">[-] MINIMIZE</button>
        </div>
        <div class="termBody" id="localTerminalContentText"></div>
      </div>
      
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
    var isTerminalMinimized = false;
    
    document.getElementById("localTerminalContentText").textContent = {safe_terminal_output};
    
    function toggleLocalTerminalState() {{
      var tBody = document.getElementById("localTerminalContentText");
      var btn = document.getElementById("stateToggleActionBtn");
      var title = document.getElementById("headerLabelTitle");
      
      if(!isTerminalMinimized) {{
        tBody.style.display = "none";
        btn.innerText = "[+] UNMINIMIZE";
        btn.style.color = "#1fec79";
        btn.style.borderColor = "#1fec79";
        title.innerText = "📺 TERM (MINIMIZED)";
        isTerminalMinimized = true;
      }} else {{
        tBody.style.display = "block";
        btn.innerText = "[-] MINIMIZE";
        btn.style.color = "#ff0055";
        btn.style.borderColor = "#ff0055";
        title.innerText = "📺 MONITOR TERMINAL FEED";
        isTerminalMinimized = false;
      }}
    }}

    var workspaceDiv = document.getElementById('blocklyDiv');
    var termWindow = document.getElementById('integratedTerminalBlock');
    
    var currentTermX = 450;
    var currentTermY = 150;
    
    var isDraggingWindow = false;
    var startX, startY;

    document.getElementById("terminalHeader").onmousedown = function(e) {{
      if(e.target.className === "windowCtrlBtn") return;
      isDraggingWindow = true;
      startX = e.clientX - currentTermX;
      startY = e.clientY - currentTermY;
      e.preventDefault();
    }};

    document.onmousemove = function(e) {{
      if (!isDraggingWindow) return;
      currentTermX = e.clientX - startX;
      currentTermY = e.clientY - startY;
      termWindow.style.left = currentTermX + 'px';
      termWindow.style.top = currentTermY + 'px';
    }};

    document.onmouseup = function() {{
      isDraggingWindow = false;
    }};

    // Inject Non-Core blockly definitions from Function.py
    {Function.BLOCKLY_INJECTS}

    // --- Inject Workspace Engine ---
    var workspace = Blockly.inject('blocklyDiv', {{
      toolbox: document.getElementById('toolbox'),
      grid: {{ spacing: 25, length: 3, colour: '#1f2833', snap: true }}, 
      trashcan: true
    }});

    // --- HYDRATION PROTOCOL ---
    try {{
      var initialXmlText = {safe_xml_state};
      if (initialXmlText && initialXmlText.trim() !== "") {{
        var dom = Blockly.utils.xml.textToDom(initialXmlText);
        Blockly.Xml.domToWorkspace(dom, workspace);
      }}
    }} catch (err) {{
      console.error("Hydration Layer Failure:", err);
    }}

    function processLiveDebugCompilations() {{
      var allBlocks = workspace.getAllBlocks(false);
      var generatedPythonCode = "";
      var sequenceFound = false;
      
      for (var i = 0; i < allBlocks.length; i++) {{
        if (allBlocks[i].type === 'when_sequence_activated') {{
          sequenceFound = true;
          generatedPythonCode += Blockly.Python.blockToCode(allBlocks[i]);
          var nextBlock = allBlocks[i].getNextBlock();
          while(nextBlock) {{
            generatedPythonCode += Blockly.Python.blockToCode(nextBlock);
            nextBlock = nextBlock.getNextBlock();
          }}
        }}
      }}
      
      var xmlDom = Blockly.Xml.workspaceToDom(workspace);
      var currentXmlText = Blockly.Xml.domToText(xmlDom);
      
      if(sequenceFound) {{
        var targetUrl = window.parent.location.origin + window.parent.location.pathname + "?payload_matrix=" + encodeURIComponent(generatedPythonCode) + "&xml_matrix=" + encodeURIComponent(currentXmlText);
        if(window.parent.location.search !== "?payload_matrix=" + encodeURIComponent(generatedPythonCode) + "&xml_matrix=" + encodeURIComponent(currentXmlText)) {{
           window.parent.history.replaceState({{}}, '', targetUrl);
        }}
      }}
    }}

    workspace.addChangeListener(function(e) {{
      if (e.type === Blockly.Events.BLOCK_CREATE || e.type === Blockly.Events.BLOCK_MOVE || e.type === Blockly.Events.BLOCK_CHANGE || e.type === Blockly.Events.BLOCK_DELETE) {{
        processLiveDebugCompilations();
      }}
    }});
    
    setInterval(processLiveDebugCompilations, 700);
  </script>
</body>
</html>
"""

components.html(blockly_html_payload, height=900, scrolling=False)

# Lower Utility Controls Zone
st.markdown("---")
st.markdown("### 🖥️ Main Engine Pipeline Terminal")

with st.expander("📋 View Compiled Execution Code Output Stream", expanded=False):
    st.session_state["synced_workspace_code"] = st.text_area(
        "Live Track Payload Manifest", 
        value=st.session_state["synced_workspace_code"], 
        height=150
    )

if st.button("⚡ Run Block Automation Flow", type="primary", use_container_width=True):
    code_to_run = st.session_state["synced_workspace_code"].strip()
    if not code_to_run or "Sequence Active" not in code_to_run:
        st.error("❌ Pipeline Error: Drag and chain tools directly underneath the 'Sequence Start' trigger block first!")
    else:
        st.session_state["terminal_history_output"] = "🛰️ STREAMING PASSED ASSET DATA SECTIONS...\n-----------------------------------------\n"
        try:
            # Execute dynamically within Function.py's namespace environment mapping
            exec_scope = {"run_scan": Function.run_scan}
            exec(code_to_run, exec_scope)
            st.success("🟢 Execution automation run complete! Check terminal view log contents.")
            st.rerun()
        except Exception as runtime_err:
            st.error(f"💥 PIPELINE BREAK: {str(runtime_err)}")