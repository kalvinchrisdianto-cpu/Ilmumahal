import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Memuat API Key (Prioritas: Secrets Streamlit, lalu .env)
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key tidak ditemukan! Masukkan di Secrets Streamlit atau file .env")
    st.stop()

# 2. Konfigurasi Model (Menggunakan Generasi 2)
generation_config = {
    "temperature": 0.8,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 4096,
}

# Inisialisasi model
# Gunakan 'gemini-2.0-flash-exp' untuk performa tercepat generasi 2
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    generation_config=generation_config,
    system_instruction="Anda adalah Guru Biologi Profesional. "
                       "Gunakan bahasa yang ringkas, singkat,  dan mudah dipahami. "

)

# 3. UI Streamlit
st.set_page_config(page_title="Guru AI Gen 2.5", page_icon="🎓")
st.title("🎓 Guru Biologi")

# Inisialisasi riwayat chat (Agar Komunikasi 2 Arah)
if "chat_session" not in st.session_state:
    # Memulai session chat pertama kali
    st.session_state.chat_session = model.start_chat(history=[])

# Menampilkan riwayat chat dari session_state
for message in st.session_state.chat_session.history:
    # Konversi label role dari Google ke Streamlit
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# 4. Input dan Respon
if prompt := st.chat_input("Tanyakan materi pelajaran di sini..."):
    # Tampilkan pesan user di UI
    st.chat_message("user").markdown(prompt)
    
    # Kirim pesan ke model dalam session yang sama
    with st.chat_message("assistant"):
        try:
            # Menggunakan stream untuk pengalaman interaktif
            response = st.session_state.chat_session.send_message(prompt, stream=True)
            
            # Memproses potongan teks yang masuk (streaming)
            full_response = ""
            placeholder = st.empty()
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Maaf, terjadi kendala teknis: {str(e)}")
