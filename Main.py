import streamlit as st
import streamlit.components.v1 as components
import os

# 1. Page Configuration
st.set_page_config(layout="wide", page_title="EZHack Platform")

# 2. Main Title
st.title("⚡ EZHack: Visual Pentest Builder")

# 3. Sidebar for execution
st.sidebar.header("Execution Controls")
if st.sidebar.button("Run Pentest Sequence"):
    st.sidebar.info("Triggering logic from tools/...")
    # This is where we will hook up your actual tools later

# 4. Blockly Renderer
def render_blockly():
    # Looks for your file in the 'assets' folder
    blockly_path = "assets/blockly.html"
    if os.path.exists(blockly_path):
        with open(blockly_path, "r") as f:
            components.html(f.read(), height=600)
    else:
        st.error(f"Could not find {blockly_path}. Please make sure the assets folder exists.")

# 5. Main Layout
col1, col2 = st.columns([4, 1])

with col1:
    st.subheader("Visual Workspace")
    render_blockly()

with col2:
    st.subheader("Toolbox")
    st.write("Drag and drop your pentest blocks here.")