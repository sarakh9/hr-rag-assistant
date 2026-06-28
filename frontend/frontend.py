# chat_ui.py
import os

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import streamlit as st
from PIL import Image


def get_assistant_answer() -> str:
    b = os.getenv("api",)
    url = os.getenv("ASSISTANT_API_URL", "http://127.0.0.1:8000/chat")
    payload = {"conversation": st.session_state.conversation}

    try:
        response = requests.post(url, json=payload, timeout=60)
        
        print("Status code:", response.status_code)
        print("Headers:", response.headers)
        print("Body:", response.text)
        
        # Check if the backend returned a successful 200 OK status
        if response.status_code == 200:
            return response.json()["assistant_response"]["content"]
        else:
            # Safely extract the backend error message if available
            error_msg = response.json().get("error", "Unknown backend error")
            return f"⚠️ Backend Error ({response.status_code}): {error_msg}"
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Connection failed: {e}")
        return f"You have reached your free limit⚠️"


@st.cache_data
def load_icon():
    file_path = "src/img/logo.png"
    return Image.open(file_path)


@st.cache_data
def load_banner():
    file_path = "src/img/logo.png"
    return Image.open(file_path)


HR_icon = load_icon()
HR_banner = load_banner()

st.image(HR_banner)

if "conversation" not in st.session_state:
    st.session_state.conversation = []

for msg in st.session_state.conversation:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant", avatar=HR_icon):
            st.markdown(msg["content"])
st.title()
st.title("Your HR assistant", Width="stretch", TextAlignment="midle")
prompt = st.chat_input("How can I help you?")

if prompt:
    # 1. Append and display User Message
    st.session_state.conversation.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Fetch the assistant's response (now a string!)
    answer_text = get_assistant_answer()
    
    # 3. Display the Assistant Message using the string directly
    with st.chat_message("assistant", avatar=HR_icon):
        st.markdown(answer_text)  # <-- Fixed: No more ["content"] here
        
    # 4. Properly format it as a dictionary before saving it to history
    st.session_state.conversation.append({"role": "assistant", "content": answer_text})
    
    # 5. Clear conversation if it exceeds 10 messages
    st.session_state.conversation = st.session_state.conversation[-10:]