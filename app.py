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

# Konfigurasi Model
generation_config = {
    "temperature": 0.7,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # Disarankan menggunakan 1.5-flash untuk stabilitas file upload
    generation_config=generation_config,
    system_instruction="Anda adalah Guru Biologi Profesional. Jawab pertanyaan dengan analogi sederhana dan bahasa yang mudah dipahami anak-anak."
)

st.set_page_config(page_title="Guru Biologi", page_icon="🎓", layout="wide")

# --- MENU RIWAYAT CHAT (SIDEBAR) ---
with st.sidebar:
    st.title("📜 Riwayat Chat")
    if st.button("🗑️ Hapus Semua Riwayat"):
        st.session_state.chat = model.start_chat(history=[])
        st.rerun()
    
    st.divider()
    st.info("Riwayat percakapan Anda tersimpan di sini selama sesi aktif.")

st.title("🎓 Tanya Guru AI Biologi")

# Memori 2 Arah
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

# Tampilkan history
for msg in st.session_state.chat.history:
    role = "assistant" if msg.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(msg.parts[0].text)

# --- FITUR UPLOAD & INPUT (BERDAMPINGAN) ---
# Membuat dua kolom: satu untuk chat input (lebar), satu untuk upload file (kecil)
col_input, col_file = st.columns([4, 1])

with col_file:
    uploaded_file = st.file_uploader("", label_visibility="collapsed", type=["pdf", "png", "jpg", "jpeg", "txt"])

with col_input:
    prompt = st.chat_input("Tanya apa hari ini?")

# Logika Pengiriman Pesan
if prompt:
    st.chat_message("user").markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            content_to_send = [prompt]
            
            # Jika ada file yang diunggah, masukkan ke konten yang dikirim
            if uploaded_file is not None:
                file_bytes = uploaded_file.read()
                content_to_send.append({
                    "mime_type": uploaded_file.type,
                    "data": file_bytes
                })
