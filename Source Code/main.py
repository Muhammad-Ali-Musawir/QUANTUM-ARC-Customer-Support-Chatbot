import streamlit as st
from ProgramEngine import get_chatbot_response
import base64
import json
from datetime import datetime
from typing import Generator  # Add for type hinting

def get_base64_image(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Page config
st.set_page_config(
    page_title="Quantum Arc Support Chatbot",
    layout="centered",
    page_icon="Source Code/Assets/icon.ico"
)

# Logo
logo_base64 = get_base64_image("Source Code/Assets/logo.png")
st.markdown(
    f"""
    <div style="display: flex; align-items: center; white-space: nowrap; overflow: hidden;">
        <img src="data:image/png;base64,{logo_base64}" width="72" style="margin-right: 10px;">
        <span style="font-size: 2em; font-weight: bold;">Quantum Arc: Customer Support Chatbot</span>
    </div>
    """,
    unsafe_allow_html=True
)
st.caption("Ask anything about products, policies, or help — Quantum Arc is here to assist you!")

# Session state setup
if "history" not in st.session_state:
    st.session_state.history = []

# Show chat history
for turn in st.session_state.history:
    with st.chat_message(turn["role"], avatar="🧠" if turn["role"] == "user" else "🤖"):
        st.markdown(turn["content"])

# Chat input
user_input = st.chat_input("Ask your question here...")

if user_input:
    with st.chat_message("user", avatar="🧠"):
        st.markdown(user_input)

    try:
        with st.spinner("💬 Thinking..."):
            response, updated_history, is_fallback = get_chatbot_response(user_input, st.session_state.history)

        # If the response is an error or warning, show it separately
        if isinstance(response, str) and ("⚠️" in response or "❌" in response):
            st.warning(response)
        else:
            with st.chat_message("assistant", avatar="🤖"):
                if isinstance(response, str):
                    st.markdown(response)
                else:
                    # Stream the response
                    st.write_stream(response)
            st.session_state.history = updated_history

    except Exception as e:
        st.error(f"❌ Error: {e}")

