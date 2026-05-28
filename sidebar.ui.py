import streamlit as st

def render_copilot(ai_engine):
    with st.sidebar:
        # The Icon (using emoji for a clean, pro look)
        st.subheader("🤖 Horizon Copilot")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display Chat History
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # The Text Box (Chat Input)
        if prompt := st.chat_input("Ask about targets..."):
            # Add to UI
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get AI response
            with st.chat_message("assistant"):
                response = ai_engine.analyze(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})