import streamlit as st
import sys
import os

# Let the frontend import from backend/
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
from pipeline import answer

st.set_page_config(page_title="Msaidizi — Campus Assistant", page_icon="🎓")
st.title("🎓 Msaidizi")
st.caption("Ask about exams, timetables, or campus info — English au Kiswahili")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.spinner("Thinking..."):
        response = answer(prompt)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)