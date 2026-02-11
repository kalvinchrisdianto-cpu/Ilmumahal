import streamlit as st
import google.generativeai as genai
import os

# Mengambil API Key langsung dari Streamlit Secrets (Lebih aman untuk Cloud)
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key tidak ditemukan. Sila masukan GEMINI_API_KEY di bagian Settings > Secrets di Streamlit Cloud.")
    st.stop()

# Konfigurasi Model
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", # Gunakan versi flash agar cepat dan stabil
    system_instruction="Anda adalah seorang Guru Biologi Profesional. Jawaban yang anda berikan memuat sebuah analogi sederhana dan bahasa yang mudah dipahami anak anak."
)

st.set_page_config(page_title="Tanya Guru AI Biologi", page_icon="🎓")
st.title("🎓 Chat dengan Guru AI Biologi")

# Inisialisasi riwayat obrolan (2-arah)
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Menampilkan riwayat chat
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# Input pengguna
if prompt := st.chat_input("Apa yang ingin kamu tanyakan hari ini?"):
    st.chat_message("user").markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            # Respon streaming agar lebih interaktif
            response = st.session_state.chat_session.send_message(prompt, stream=True)
            full_response = st.write_stream(response)
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
