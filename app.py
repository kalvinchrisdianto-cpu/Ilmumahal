import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from PIL import Image

# 1. Setup API
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key not found!")
    st.stop()

# 2. Model Config
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "max_output_tokens": 4096,
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash", # Updated to a valid version
    generation_config=generation_config,
    system_instruction="Anda adalah Guru Biologi Profesional. "
                       "Bantu siswa memahami konsep biologi melalui teks atau gambar diagram. "
                       "Gunakan bahasa yang edukatif namun santai."
)

# 3. UI Layout
st.set_page_config(page_title="Guru Biologi AI", page_icon="🔬")
st.title("🔬 Guru Biologi Virtual")

# Sidebar for Image Uploads and Reset
# 1. Update the uploader in your sidebar
with st.sidebar:
    st.header("Upload Materi")
    uploaded_file = st.file_uploader(
        "Upload gambar, PDF, video, atau audio (Max 20MB)", 
        type=["jpg", "jpeg", "png", "pdf", "mp4", "mov", "mp3", "wav"]
    )
    
    # Preview logic
    if uploaded_file:
        if uploaded_file.type.startswith("image/"):
            st.image(uploaded_file, caption="Gambar Terupload")
        elif uploaded_file.type == "application/pdf":
            st.info("📄 PDF Terupload: Model akan membaca isi dokumen ini.")
        elif uploaded_file.type.startswith("video/"):
            st.video(uploaded_file)
        elif uploaded_file.type.startswith("audio/"):
            st.audio(uploaded_file)

# 2. Update the Processing Logic (Send to Gemini)
if prompt := st.chat_input("Tanyakan sesuatu..."):
    st.chat_message("user").markdown(prompt)
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        # Prepare content list for Gemini
        content_to_send = [prompt]
        
        if uploaded_file:
            # Convert uploaded file to bytes and identify mime type
            file_bytes = uploaded_file.read()
            content_to_send.append({
                "mime_type": uploaded_file.type,
                "data": file_bytes
            })

        try:
            response = st.session_state.chat_session.send_message(content_to_send, stream=True)
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Error: {e}")

# Initialize Chat Session
if "chat_session" not in st.session_state:
    st.session_state.chat_session = model.start_chat(history=[])

# Display Chat History
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# 4. Chat & Image Logic
if prompt := st.chat_input("Tanyakan sesuatu..."):
    st.chat_message("user").markdown(prompt)
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        
        # Prepare content: Text only or Text + Image
        if uploaded_file:
            img = Image.open(uploaded_file)
            content = [prompt, img]
        else:
            content = prompt

        try:
            # Send to model
            response = st.session_state.chat_session.send_message(content, stream=True)
            
            for chunk in response:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
