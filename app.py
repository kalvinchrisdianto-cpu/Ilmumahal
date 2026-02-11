import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key belum disetting di Secrets Streamlit!")
    st.stop()

# 2. Konfigurasi Model
generation_config = {
    "temperature": 0.7,
    "max_output_tokens": 2048,
}

# Catatan: Gunakan "gemini-1.5-flash" atau "gemini-2.0-flash-exp" 
# karena versi 2.5 belum dirilis secara resmi di publik API.
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    generation_config=generation_config,
    system_instruction="Anda adalah Guru Biologi Profesional. Jawab pertanyaan dengan analogi sederhana dan bahasa yang mudah dipahami anak-anak."
)

st.set_page_config(page_title="Guru Biologi", page_icon="🎓", layout="wide")

# --- SIDEBAR: Menu Riwayat & Unggah File ---
with st.sidebar:
    st.title("📂 Menu Pembelajaran")
    
    # Fitur Unggah File
    uploaded_file = st.file_uploader(
        "Unggah materi biologi (Gambar/PDF/Teks)", 
        type=["pdf", "png", "jpg", "jpeg", "txt"]
    )
    
    if uploaded_file:
        st.info(f"File Terdeteksi: {uploaded_file.name}")

    st.divider()
    
    # Fitur Riwayat Chat: Tombol Reset
    st.subheader("Riwayat Sesi")
    if st.button("🗑️ Mulai Sesi Baru / Hapus Riwayat"):
        st.session_state.chat = model.start_chat(history=[])
        st.rerun()
    
    st.caption("Menghapus riwayat akan menyegarkan ingatan Guru AI.")

# --- TAMPILAN UTAMA ---
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
        try:
            # Menggabungkan Teks dan File jika ada
            content_to_send = [prompt]
            if uploaded_file:
                # Membaca file sebagai bytes untuk dikirim ke Gemini
                file_bytes = uploaded_file.read()
                content_to_send.append({"mime_type": uploaded_file.type, "data": file_bytes})
            
            # Mengirim pesan ke AI
            response = st.session_state.chat.send_message(content_to_send, stream=True)
            full_response = st.write_stream(response)
            
        except Exception as e:
            st.error(f"Terjadi kesalahan teknis: {str(e)}")
