import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key belum disetting di Secrets Streamlit!")
    st.stop()

# Konfigurasi Model - Menggunakan 1.5 Flash yang paling stabil untuk deploy
generation_config = {
    "temperature": 0.7,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", # Sangat stabil & cepat
    generation_config=generation_config,
    system_instruction="Anda adalah Guru Biologi Profesional. Jawab pertanyaan dengan analogi sederhana dan bahasa yang mudah dipahami anak-anak."
)

st.set_page_config(page_title="Guru Biologi", page_icon="🎓")
st.title("🎓 Tanya Guru AI Biologi")

# Memori 2 Arah
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# Tampilkan history
for msg in st.session_state.chat.history:
    role = "assistant" if msg.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(msg.parts[0].text)

# Input User
if prompt := st.chat_input("Tanya apa hari ini?"):
    st.chat_message("user").markdown(prompt)
    
    with st.chat_message("assistant"):
        response = st.session_state.chat.send_message(prompt, stream=True)
        full_response = st.write_stream(response)


