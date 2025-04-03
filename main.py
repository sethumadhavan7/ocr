import os
from dotenv import load_dotenv
import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import io
from gtts import gTTS
from io import BytesIO

# Load environment variables from .env
load_dotenv()
API_KEY = os.getenv("API_KEY")  # Your Gemini Flash API key if needed

st.title("PDF Document OCR Extraction with Text-to-Speech")

st.markdown("""
Upload a PDF file, and the app will:
1. Extract text from each page (OCR)
2. Convert the extracted text to speech
""")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    try:
        # Open the PDF file using PyMuPDF
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        extracted_text = ""
        st.info(f"Processing {len(doc)} pages...")
        
        # Process each page
        for i, page in enumerate(doc):
            # Get the page as a pixmap (image)
            pix = page.get_pixmap()
            
            # Convert pixmap to PIL Image
            img_bytes = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_bytes))
            
            # Perform OCR using pytesseract
            page_text = pytesseract.image_to_string(img)
            extracted_text += f"\n\n--- Page {i+1} ---\n{page_text}"
            
            # Optional: Show progress
            st.write(f"Processed page {i+1}/{len(doc)}")
        
        st.success("Text extraction complete!")
        st.text_area("Extracted Text", value=extracted_text, height=400)
        
        # Text-to-Speech Section
        st.subheader("Text-to-Speech Conversion")
        
        if len(extracted_text) > 0:
            # Language selection (default: English)
            lang = st.selectbox("Select language", ['en', 'es', 'fr', 'de', 'hi'], index=0)
            
            if st.button("Convert to Speech"):
                with st.spinner("Generating audio..."):
                    # Create gTTS object
                    tts = gTTS(text=extracted_text, lang=lang, slow=False)
                    
                    # Save to bytes buffer
                    audio_bytes = BytesIO()
                    tts.write_to_fp(audio_bytes)
                    audio_bytes.seek(0)
                    
                    # Play audio
                    st.audio(audio_bytes, format='audio/mp3')
                    
                    # Download button
                    st.download_button(
                        label="Download Audio (MP3)",
                        data=audio_bytes,
                        file_name="extracted_text.mp3",
                        mime="audio/mpeg"
                    )
    
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("Please ensure you have Tesseract OCR installed: https://github.com/tesseract-ocr/tesseract")