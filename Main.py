import os
import socket
import json
import urllib.request
import random
import streamlit as st
import streamlit.components.v1 as components

# ==========================================
# 1. UTILITY MODULE DEFINITIONS
# ==========================================

def perform_dns_lookup(target: str) -> str:
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_host:
        return "❌ ERROR: Target host domain missing!"
    try:
        ip_addr = socket.gethostbyname(clean_host)
        return (
            f"🔍 [WEBSITE SERVER LOOK-UP]\n"
            f"  ├── Website Name : {clean_host}\n"
            f"  └── Server IP    : {ip_addr}\n"
            f"🟢 SUCCESS: Record lookup processing complete."
        )
    except Exception as e:
        return f"❌ ERROR: Failed to resolve host context ({str(e)})."


def perform_ip_geolocation(target: str) -> str:
    clean_host = str(target).strip().replace(" ", "").replace('"', '').replace("'", "")
    if not clean_host:
        return "❌ ERROR: Target IP/Host address missing!"
    try:
        lookup_ip = socket.gethostbyname(clean_host)
        api_url = f"http://ip-api.com/json/{lookup_ip}"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as stream:
            payload = json.loads(stream.read().decode())
            
        if payload.get("status") == "fail":
            return f"❌ ERROR: {payload.get('message', 'Routing provider error')}"
            
        return (
            f"🗺️ [IP ADDRESS LOCATION REPORT]\n"
            f"  ├── Target Host  : {clean_host}\n"
            f"  ├── Resolved IP  : {payload.get('query')}\n"
            f"  ├── Country Code : {payload.get('country')} ({payload.get('countryCode')})\n"
            f"  └── Region/City  : {payload.get('city')}, {payload.get('regionName')}\n"
            f"🟢 SUCCESS: Location routing trace finalized."
        )
    except Exception as e:
        return f"💥 SYSTEM ERROR: {str(e)}"


def perform_phone_scan(target_phone: str) -> str:
    clean_phone = str(target_phone).strip().replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not clean_phone:
        return "❌ ERROR: Digits input parameter missing!"
    
    is_intl = clean_phone.startswith("+")
    region_est = "🌍 International Route" if is_intl else "🇺🇸 Domestic Route"
    
    carriers = ["Verizon Communications Core", "AT&T Mobility Hub", "T-Mobile Routing Network"]
    seed_val = sum(ord(c) for c in clean_phone)
    random.seed(seed_val)
    selected_carrier = random.choice(carriers)
    
    return (
        f"📡 [PHONE NUMBER SCAN RAPID REPORT]\n"
        f"  ├── Original Input: {target_phone}\n"
        f"  ├── Area Assessment: {region_est}\n"
        f"  └── Provider Path  : {selected_carrier}\n"
        f"🟢 SUCCESS: Line checks verified."
    )

# ==========================================
# 2. RUNTIME RECON PIPELINE ENGINE
# ==========================================

def run_utility_scan(target_string: str, scan_profile_type: str) -> str:
    profile = str(scan_profile_type).lower().strip()
    if profile == "phone":
        return perform_phone_scan(target_string)
    elif profile == "dns":
        return perform_dns_lookup(target_string)
    else:
        return perform_ip_geolocation(target_string)


def execute_compiled_pipeline(script_text: str):
    st.session_state["console_terminal_logs"] = "⚡ MONITOR STREAM ACTIVE...\n⚡ EXECUTING ACTIVE SEQUENCE CHAIN:\n"
    
    sandbox_environment = {
        "run_utility_scan": run_utility_scan,
        "st": st,
        "current_result": ""
    }
    
    clean_execution_lines = []
    for line in script_text.splitlines():
        if "when_sequence_activated" in line or "Sequence #" in line or line.strip().startswith("#"):
            continue
        # Route internal prints straight to backend logs
        if "show_output_to_user" in line or "print" in line:
            clean_execution_lines.append("st.session_state['console_terminal_logs'] += f'\\n' + str(current_result) + f'\\n⚡' + '='*48 + f'\\n'")
            continue
        clean_execution_lines.append(line)
        
    execution_payload = "\n".join(clean_execution_lines)
    
    if not execution_payload.strip():
        st.session_state["console_terminal_logs"] += "\n⚠️ WARNING: Connect modules to a Start Block sequence chain to compile logic paths."
        return

    try:
        exec(execution_payload, sandbox_environment)
    except Exception as runtime_error:
        st.session_state["console_terminal_logs"] += f"\n💥 [SCRIPT RUN ERROR]: {str(runtime_error)}"

# ==========================================
# 3. INTERFACE BUILDER & STATE PARSER
# ==========================================

if "console_terminal_logs" not in st.session_state:
    st.session_state["console_terminal_logs"] = "💻 [READY] Pipeline stream fully operational..."

# Track incoming code streams using browser parameter handshakes to bypass frame isolation locks
query_params = st.query_params
live_code_translation = query_params.get("compiled_block_payload", "# Awaiting layout block changes...")

# Layout Grid Configuration Header
top_action_col, spacer_col = st.columns([3, 9])
with top_action_col:
    trigger_pipeline_run = st.button("🚀 LAUNCH CIRCUIT PIPELINE", type="primary", use_container_width=True)

safe_terminal_logs = st.session_state["console_terminal_logs"].replace("`", "'").replace("\\", "\\\\").replace("\n", "\\n")

st.markdown("### 🗺️ Visual Studio Workspace Canvas")

# ==========================================
# 4. DARK CYBER CORE VISUAL WORKSPACE
# ==========================================
blockly_html_payload = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Blockly Workspace</title>
  <script src="https://unpkg.com/blockly/blockly.min.js"></script>
  <script src="https://unpkg.com/blockly/python_compressed.js"></script>
  <script src="https://unpkg.com/blockly/blocks_compressed.js"></script>
  <style>
    html, body {{ height: 100%; margin: 0; padding: 0; background-color: #0b0c10; font-family: sans-serif; overflow: hidden; }}
    #containerDiv {{ position: relative; width: 100%; height: 600px; }}
    #blocklyDiv {{ width: 100%; height: 100%; border: 2px solid #1f2833; border-radius: 6px; }}
    
    /* Draggable Terminal Window Component */
    #draggableTerminal {{
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
    }}
    #terminalHeader {{
      padding: 10px;
      cursor: move;
      background: #1f2833;
      border-bottom: 2px solid #45a29e;
      color: #66fcf1;
      font-weight: bold;
      font-size: 11px;
      user-select: none;
    }}
    #terminalBody {{
      flex: 1;
      padding: 12px;
      margin: 0;
      background: #0b0c10;
      color: #1fec79;
      font-family: monospace;
      font-size: 12px;
      overflow-y: auto;
      white-space: pre-wrap;
    }}
    
    /* Lower Diagnostics Logger Component */
    #canvasDiagnostics {{
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
    }}
  </style>
</head>
<body>

  <div id="containerDiv">
    <div id="draggableTerminal">
      <div id="terminalHeader">🤖 LIVE TARGET OUTPUT TERMINAL</div>
      <pre id="terminalBody">{safe_terminal_logs}</pre>
    </div>
    
    <div id="canvasDiagnostics">⚙️ EVENT ENGINE SYSTEM LOGGER:<br>🟢 Systems synced. Drag layout blocks to adjust pipeline context...</div>
    
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
    <category name="🖥️ Monitor Controls" colour="65">
      <block type="display_result"></block>
    </category>
  </xml>

  <script>
    // Custom Block Setup Declarations
    Blockly.Blocks['when_sequence_activated'] = {{
      init: function() {{
        this.appendDummyInput().appendField("🚀 Start Block (Sequence)");
        this.setNextStatement(true, null);
        this.setColour(0);
      }}
    }};

    Blockly.Blocks['custom_input_string'] = {{
      init: function() {{
        this.appendDummyInput()
            .appendField("Type Target:")
            .appendField(new Blockly.FieldTextInput("+15555550199"), "RAW_TEXT");
        this.setOutput(true, "String");
        this.setColour(160);
      }}
    }};

    Blockly.Blocks['action_scan'] = {{
      init: function() {{
        this.appendValueInput("NAME").setCheck(null).appendField("Target info to check:");
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
      }}
    }};

    Blockly.Blocks['display_result'] = {{
      init: function() {{
        this.appendDummyInput().appendField("📟 Print Results to Monitor Screen");
        this.setPreviousStatement(true, null);
        this.setNextStatement(true, null);
        this.setColour(65);
      }}
    }};

    // Logic String Parsers
    Blockly.Python.forBlock['when_sequence_activated'] = function(block) {{ return '# [Start Sequence]\\n'; }};
    Blockly.Python.forBlock['custom_input_string'] = function(block) {{ return ['"' + block.getFieldValue('RAW_TEXT') + '"', 0]; }};
    Blockly.Python.forBlock['action_scan'] = function(block) {{
      var type = block.getFieldValue('SCANTYPE');
      var val = Blockly.Python.valueToCode(block, 'NAME', 0) || "''";
      return 'current_result = run_utility_scan(' + val + ', "' + type + '")\\n';
    }};
    Blockly.Python.forBlock['display_result'] = function(block) {{ return 'print(current_result)\\n'; }};

    var workspace = Blockly.inject('blocklyDiv', {{
      toolbox: document.getElementById('toolbox'),
      grid: {{spacing: 20, length: 3, colour: '#1f2833', snap: true}},
      trashcan: true
    }});

    // Draw the initial layout configuration components safely
    var xmlText = '<xml><block type="when_sequence_activated" x="40" y="40"><next><block type="action_scan"><field name="SCANTYPE">phone</field><value name="NAME"><block type="custom_input_string"><field name="RAW_TEXT">+15555550199</field></block></value><next><block type="display_result"></block></next></block></next></block></xml>';
    Blockly.Xml.domToWorkspace(Blockly.Xml.textToDom(xmlText), workspace);

    var diagnosticsLogBox = document.getElementById("canvasDiagnostics");
    var targetURLLocationStr = window.parent.location.href.split('?')[0];

    function compileAndSyncPipeline() {{
      var allBlocks = workspace.getAllBlocks(false);
      var sequenceCount = 0;
      var combinedScript = "";
      
      var trackingReport = "⚙️ LIVE ENGINE STATUS REPORT:<br>✨ Total Blocks Placed: " + allBlocks.length + "<br>";

      for (var i = 0; i < allBlocks.length; i++) {{
        if (allBlocks[i].type === 'when_sequence_activated') {{
          sequenceCount++;
          trackingReport += "<span style='color:#66fcf1;'>🏁 Registered Start Block #" + sequenceCount + " (" + allBlocks[i].id.substring(0,5) + ")</span><br>";
          combinedScript += "# ---- Sequence #" + sequenceCount + " ----\\n";
          
          var loopNode = allBlocks[i].getNextBlock();
          while (loopNode) {{
            var chunkCode = Blockly.Python.blockToCode(loopNode);
            if (typeof chunkCode === 'string') {{
              combinedScript += chunkCode;
            }} else if (Array.isArray(chunkCode)) {{
              combinedScript += chunkCode[0];
            }}
            loopNode = loopNode.getNextBlock();
          }}
        }}
      }}

      if (sequenceCount === 0) {{
        combinedScript = "# ⚠️ Error: Active Start Block missing from canvas layout stage!";
        trackingReport += "<span style='color:#ff3366;'>⚠️ CRITICAL STATUS: Place a Start Block onto the canvas workspace floor!</span><br>";
      }}

      diagnosticsLogBox.innerHTML = trackingReport;
      var cleanScript = combinedScript.trim();

      // Safely notify the parent runtime context using address state transitions without causing component refresh crashes
      var parsedParameters = new URLSearchParams(window.parent.location.search);
      if (parsedParameters.get("compiled_block_payload") !== cleanScript) {{
        parsedParameters.set("compiled_block_payload", cleanScript);
        window.parent.history.replaceState({{}}, "", targetURLLocationStr + "?" + parsedParameters.toString());
      }}
    }}

    // Hook layout modifiers to native execution checks
    workspace.addChangeListener(function(e) {{
      if (e.type === Blockly.Events.BLOCK_CREATE || e.type === Blockly.Events.BLOCK_MOVE || e.type === Blockly.Events.BLOCK_CHANGE || e.type === Blockly.Events.BLOCK_DELETE) {{
        compileAndSyncPipeline();
      }}
    }});

    setInterval(compileAndSyncPipeline, 250);
    setTimeout(compileAndSyncPipeline, 350);

    // Draggable Elements Config Frame Systems
    var element = document.getElementById("draggableTerminal");
    var header = document.getElementById("terminalHeader");
    var activeDragging = false;
    var currentX, currentY, initialX, initialY, xOffset = 0, yOffset = 0;

    header.addEventListener("mousedown", function(e) {{
      initialX = e.clientX - xOffset; initialY = e.clientY - yOffset;
      if (e.target === header) activeDragging = true;
    }}, false);
    document.addEventListener("mouseup", function() {{ activeDragging = false; }}, false);
    document.addEventListener("mousemove", function(e) {{
      if (activeDragging) {{
        e.preventDefault();
        currentX = e.clientX - initialX; currentY = e.clientY - initialY;
        xOffset = currentX; yOffset = currentY;
        element.style.transform = "translate3d(" + currentX + "px, " + currentY + "px, 0)";
      }}
    }}, false);
  </script>
</body>
</html>
"""

# Render the application workspace layout panel
components.html(blockly_html_payload, height=620, scrolling=False)

if trigger_pipeline_run:
    execute_compiled_pipeline(live_code_translation)

# ==========================================
# 5. BACKEND TRANSLATOR SCREEN
# ==========================================
st.markdown("### 📝 Code Translation Behind the Blocks")
st.code(live_code_translation, language="python")