import os
import json
import urllib.parse
import time
import streamlit as st
import streamlit.components.v1 as components

from dotenv import load_dotenv
from groq import Groq

# Import our complete separated block module payloads
import block_registry

# --- 1. System Setup & Workspace Configurations ---
load_dotenv()
st.set_page_config(page_title="Horizon Tactical C2 UI Workspace", layout="wide")

# Handle API connection via Groq backend distribution layers
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ai_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

MODEL_ROSTER = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant"
]

def generate_completion_with_fallback(messages):
    if not ai_client:
        return "❌ ERROR: Local host configuration failed. GROQ_API_KEY missing from context properties."
    for model_name in MODEL_ROSTER:
        try:
            response = ai_client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.2
            )
            return response.choices[0].message.content
        except Exception as model_fault:
            st.toast(f"⚠️ Model Node fault triggered, fallback redirection initiated...", icon="🔄")
            continue
    return "❌ CRITICAL: Complete model pool context exhaustion encountered. System on standby."

# Global UI layout styles
st.markdown("""
<style>
    .reportview-container .main .block-container {
        padding-top: 1rem !important;
        max-width: 95% !important;
    }
    iframe {
        border-radius: 6px;
        border: 2px dashed #00ff66 !important;
        background-color: #010101 !important;
    }
    .live-code-container {
        background-color: #030303;
        border-left: 3px solid #00ff66;
        padding: 12px;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ HORIZON RADAR OSINT WORKSPACE CONTROL LAYER")

if "system_console_history" not in st.session_state:
    st.session_state.system_console_history = "📡 Terminal ready. Wire sequence execution links to process loops..."

# --- 2. Address Query Parameter Matrix Interception ---
incoming_parameters = st.query_params
active_payload_code = incoming_parameters.get("payload_matrix", "")

if active_payload_code:
    decoded_script = urllib.parse.unquote(active_payload_code)
    console_reporting = "🚀 Intercepting Compiled Functional Automation Pipeline Pipeline Sequence...\n"
    
    execution_scope = {
        "run_scan": block_registry.run_scan,
        "time": time,
        "print_output": lambda data: data
    }
    
    try:
        lines = decoded_script.split('\n')
        for script_line in lines:
            if script_line.strip() and not script_line.strip().startswith("#"):
                execution_line = script_line.strip()
                returned_log = eval(execution_line, {"__builtins__": None}, execution_scope)
                if returned_log:
                    console_reporting += f"\n[NODE OUT]:\n{str(returned_log)}\n"
        st.session_state.system_console_history = console_reporting
    except Exception as runtime_fault:
        st.session_state.system_console_history = f"❌ RUNTIME EXCEPT STRUCTURAL COLLAPSE:\n{str(runtime_fault)}"
        
    st.query_params.clear()

# --- 3. Iframe Component Architecture HTML Payload ---
blockly_html_payload = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Blockly Core Sandbox</title>
  <script src="https://unpkg.com/blockly/blockly.min.js"></script>
  <style>
    html, body {{
      margin: 0; padding: 0; background: #000000;
      width: 100%; height: 100%; overflow: hidden;
    }}
    #workspaceArea {{
      width: 100%; height: 100vh; position: relative;
    }}
    /* Dark Cyber Theme Customisations */
    .blocklyTreeRow {{
      background-color: #050505 !important;
      color: #00ff66 !important;
      border-left: 3px solid #00ff66 !important;
      font-family: 'Courier New', monospace;
      padding: 8px 12px !important;
      margin-bottom: 4px !important;
    }}
    .blocklyTreeSelected {{
      background-color: #00ff66 !important;
      color: #000000 !important;
    }}
    .blocklyFlyoutBackground {{
      fill: #020202 !important;
      fill-opacity: 0.98 !important;
      stroke: #00ff66 !important;
    }}
  </style>
</head>
<body>

  <div id="workspaceArea"></div>

  {block_registry.TOOLBOX_XML}

  <script>
    // Inject complex definitions without simplifications
    {block_registry.BLOCK_DEFINITIONS_JS}
    {block_registry.PYTHON_GENERATORS_JS}

    window.workspace = Blockly.inject('workspaceArea', {{
      toolbox: document.getElementById('toolbox'),
      grid: {{
        spacing: 24,
        length: 3,
        colour: 'rgba(0, 255, 102, 0.1)',
        snap: true
      }},
      trashcan: true,
      zoom: {{
        controls: true,
        wheel: true,
        startScale: 1.0
      }}
    }});

    function processLiveDebugCompilations() {{
      var topBlocks = window.workspace.getTopBlocks(true);
      var generatedPythonCode = "";
      var sequenceFound = false;
      
      for (var i = 0; i < topBlocks.length; i++) {{
        if (topBlocks[i].type === 'when_sequence_activated') {{
          sequenceFound = true;
          generatedPythonCode += Blockly.Python.blockToCode(topBlocks[i]);
        }}
      }}
      
      var xmlDom = Blockly.Xml.workspaceToDom(window.workspace);
      var currentXmlText = Blockly.Xml.domToText(xmlDom);
      
      if (sequenceFound) {{
        var targetUrl = window.parent.location.origin + window.parent.location.pathname + "?payload_matrix=" + encodeURIComponent(generatedPythonCode) + "&xml_matrix=" + encodeURIComponent(currentXmlText);
        if (window.parent.location.search !== "?payload_matrix=" + encodeURIComponent(generatedPythonCode) + "&xml_matrix=" + encodeURIComponent(currentXmlText)) {{
          window.parent.history.replaceState({{}}, '', targetUrl);
        }}
      }}
    }}

    var compileTimeout = null;
    window.workspace.addChangeListener(function(e) {{
      if (e.type === Blockly.Events.BLOCK_CREATE || e.type === Blockly.Events.BLOCK_MOVE || e.type === Blockly.Events.BLOCK_CHANGE || e.type === Blockly.Events.BLOCK_DELETE) {{
        clearTimeout(compileTimeout);
        compileTimeout = setTimeout(processLiveDebugCompilations, 500);
      }}
    }});
  </script>
</body>
</html>
"""

components.html(blockly_html_payload, height=800, scrolling=False)

# --- 4. Streamlit Debug Console Terminal Panel ---
st.markdown('<div class="live-code-container">', unsafe_allow_html=True)
st.subheader("📟 OPERATIONAL TELEMETRY TERMINAL INTERCEPT")
st.code(st.session_state.system_console_history, language="bash")
st.markdown('</div>', unsafe_allow_html=True)