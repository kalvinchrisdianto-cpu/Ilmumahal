import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image

# 1. Memuat API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key tidak ditemukan!")
    st.stop()

# 2. Konfigurasi Model
generation_config = {
    "temperature": 0.8,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 4096,
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", 
    generation_config=generation_config,
    system_instruction="Anda adalah Guru Biologi Profesional. Gunakan bahasa yang ringkas dan mudah dipahami."
)

# 3. UI Streamlit
st.set_page_config(page_title="Guru AI Gen 2", page_icon="🎓")
st.title("🎓 Guru Biologi")

# Sidebar untuk Upload File (Menerima semua jenis file)
with st.sidebar:
    st.header("Upload Materi")
    uploaded_file = st.file_uploader("Pilih file (Gambar, PDF, Video, Audio, dll)", type=None) # type=None allows all files
    if uploaded_file:
        st.success(f"File terdeteksi: {uploaded_file.name}")

# Inisialisasi riwayat chat
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Menampilkan riwayat chat
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# 4. Input dan Respon
if prompt := st.chat_input("Tanyakan materi pelajaran di sini..."):
    st.chat_message("user").markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            # logic untuk mengirim pesan (Teks saja atau Teks + File)
            if uploaded_file:
                file_content = {
                    "mime_type": uploaded_file.type,
                    "data": uploaded_file.read()
                }
                response = st.session_state.chat_session.send_message([prompt, file_content], stream=True)
            else:
                response = st.session_state.chat_session.send_message(prompt, stream=True)
            
            full_response = ""
            placeholder = st.empty()
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Maaf, terjadi kendala teknis: {str(e)}")
