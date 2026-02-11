import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. API Key Setup
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key missing! Check your .env or Streamlit Secrets.")
    st.stop()

# 2. Model Configuration
generation_config = {
    "temperature": 0.7, # Slightly lower for more factual biology answers
    "top_p": 0.95,
    "max_output_tokens": 2048,
}

# Updated model name to a valid version
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    generation_config=generation_config,
    system_instruction="Anda adalah Guru Biologi Profesional. "
                       "Gunakan bahasa yang ringkas, edukatif, dan mudah dipahami."
)

# 3. UI Streamlit
st.set_page_config(page_title="Guru Biologi AI", page_icon="🌿")
st.title("🌿 Guru Biologi Virtual")

# Sidebar for controls
with st.sidebar:
    if st.button("Hapus Riwayat Chat"):
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()

# Initialize Chat Session
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Display History
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# 4. Input & Logic
if prompt := st.chat_input("Tanyakan tentang sel, genetika, atau ekosistem..."):
    st.chat_message("user").markdown(prompt)
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        try:
            # Streaming response
            response = st.session_state.chat_session.send_message(prompt, stream=True)
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Error: {e}")
