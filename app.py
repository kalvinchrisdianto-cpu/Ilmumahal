import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
# Tambahkan library ini untuk fitur suara (install: pip install streamlit-mic-recorder)
from streamlit_mic_recorder import mic_recorder

# Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key belum disetting di Secrets Streamlit!")
    st.stop()

# Konfigurasi Model
generation_config = {
    "temperature": 0.7,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # Gunakan 1.5-flash karena mendukung analisis file & suara lebih stabil
    generation_config=generation_config,
    system_instruction="Anda adalah Guru Biologi Profesional. Jawab pertanyaan dengan analogi sederhana dan bahasa yang mudah dipahami anak-anak."
)

st.set_page_config(page_title="Guru Biologi", page_icon="🎓", layout="wide")

# --- MENU RIWAYAT CHAT (Sidebar) ---
with st.sidebar:
    st.title("📚 Menu Riwayat")
    if st.button("🗑️ Hapus Riwayat Chat"):
        st.session_state.chat = model.start_chat(history=[])
        st.rerun()
    
    st.divider()
    st.write("Riwayat sesi ini:")
    if "chat" in st.session_state:
        for i, msg in enumerate(st.session_state.chat.history):
            role = "👤 Siswa" if msg.role == "user" else "🎓 Guru"
            st.caption(f"{role}: {msg.parts[0].text[:30]}...")

st.title("🎓 Tanya Guru AI Biologi")

# Memori 2 Arah
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# Tampilkan history
for msg in st.session_state.chat.history:
    role = "assistant" if msg.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(msg.parts[0].text)

# --- AREA INPUT (File, Suara, & Teks) ---
# Membuat layout kolom tepat di atas bar input chat
col_file, col_voice = st.columns([4, 1])

with col_file:
    uploaded_file = st.file_uploader("Lampirkan dokumen/gambar materi", type=["pdf", "png", "jpg", "jpeg", "txt"])

with col_voice:
    st.write("Klik untuk bicara:")
    audio_prompt = mic_recorder(start_prompt="🎤 Mulai", stop_prompt="⏹️ Berhenti", key='recorder')

# Logika Pengolahan Input
prompt = st.chat_input("Tanya apa hari ini?")

# Jika ada input suara, gunakan hasil transkrip atau data suara (memerlukan integrasi speech-to-text tambahan jika ingin teks)
# Untuk kesederhanaan, kita prioritaskan input teks atau file.
if prompt or audio_prompt:
    user_input = prompt if prompt else "Menganalisis file/suara yang dikirim..."
    
    st.chat_message("user").markdown(user_input)
    
    with st.chat_message("assistant"):
        content_parts = [user_input]
        
        # Tambahkan file ke konten jika ada
        if uploaded_file:
            file_bytes = uploaded_file.read()
            content_parts.append({"mime_type": uploaded_file.type, "data": file_bytes})
        
        # Tambahkan audio ke konten jika ada
        if audio_prompt:
            content_parts.append({"mime_type": "audio/wav", "data": audio_prompt['bytes']})
        
        try:
            response = st.session_state.chat.send_message(content_parts, stream=True)
            full_response = st.write_stream(response)
        except Exception as e:
            st.error(f"Maaf, Guru sedang lelah. Error: {e}")
