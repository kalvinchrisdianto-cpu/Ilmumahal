import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv 

# 1. Konfigurasi API Key
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key tidak ditemukan. Masukkan GEMINI_API_KEY di Secrets Streamlit.")
    st.stop()

# 2. Inisialisasi Model (Gemini 1.5 Flash mendukung berbagai jenis file/multimodal)
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    system_instruction="Anda adalah Guru Biologi profesional. Anda bisa menganalisis file yang diunggah dan menjawab pertanyaan siswa."
    "Jawaban yang anda berikan mudah dipahami oleh siswa dan jelaskan dengan analogi dengan bahasa anak sd."
)

# 3. UI Streamlit
st.set_page_config(page_title="Guru AI Biologi", page_icon="🎓", layout="wide")

# --- SIDEBAR: Menu Riwayat & Unggah File ---
with st.sidebar:
    st.title("⚙️ Menu Guru AI")
    
    # Fitur Unggah File
    uploaded_file = st.file_uploader(
        "Unggah materi (PDF, Gambar, Teks, dll.)", 
        type=["pdf", "png", "jpg", "jpeg", "txt", "docx"]
    )
    
    if uploaded_file:
        st.success(f"File '{uploaded_file.name}' berhasil diunggah!")

    st.divider()
    
    # Fitur Reset/Hapus Riwayat Chat
    if st.button("🗑️ Hapus Riwayat Chat", use_container_width=True):
        st.session_state.chat_session = model.start_chat(history=[])
        st.rerun()

st.title("🎓Guru AI Biologi ")
st.caption("Sekarang Bapak/Ibu Guru bisa membaca file yang kamu unggah!")

# 4. Inisialisasi Riwayat Chat (2-arah)
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Menampilkan riwayat chat
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# 5. Logika Input & Respon
if prompt := st.chat_input("Tanyakan sesuatu tentang materi..."):
    st.chat_message("user").markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            content_to_send = [prompt]
            
            # Jika ada file yang diunggah, masukkan ke dalam input AI
            if uploaded_file is not None:
                file_bytes = uploaded_file.read()
                # Mengonversi file ke format yang dipahami Gemini
                file_data = {"mime_type": uploaded_file.type, "data": file_bytes}
                content_to_send.append(file_data)
            
            # Respon streaming
            response = st.session_state.chat_session.send_message(content_to_send, stream=True)
            full_response = st.write_stream(response)
            
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

# Footer informasi riwayat
st.sidebar.info(f"Jumlah pesan dalam sesi ini: {len(st.session_state.chat_session.history)}")
