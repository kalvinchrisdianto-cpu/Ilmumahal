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
