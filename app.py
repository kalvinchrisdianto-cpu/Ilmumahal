import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Memuat API Key dari file .env atau Secrets
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Konfigurasi AI Studio
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key tidak ditemukan. Pastikan sudah disetting di Environment Variables.")

# 2. Pengaturan Model & Instruksi Peran (Guru)
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=generation_config,
    system_instruction="Anda adalah seorang Guru yang bijak, sabar, dan edukatif. "
                       "Tugas Anda adalah menjawab pertanyaan siswa dengan bahasa yang mudah dimengerti, "
                       "memberikan contoh, dan selalu menyemangati siswa untuk belajar."
)

# 3. UI Streamlit
st.set_page_config(page_title="Tanya Guru AI", page_icon="🎓")
st.title("🎓 Chat dengan Guru AI")
st.caption("Tanyakan apa saja, Bapak/Ibu Guru siap membantu!")

# Inisialisasi riwayat obrolan (Stateful/2-arah)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Menampilkan riwayat chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input pengguna
if prompt := st.chat_input("Apa yang ingin kamu tanyakan hari ini?"):
    # Tambah chat user ke riwayat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respon AI
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Mengirim pesan ke Gemini
        chat = model.start_chat(history=[])
        response = chat.send_message(prompt, stream=True)
        
        for chunk in response:
            full_response += chunk.text
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
    
    # Simpan respon asisten ke riwayat
    st.session_state.messages.append({"role": "assistant", "content": full_response})
