import streamlit as st
import tempfile
import os
from app.services.pdf_service import render_page_to_image, process_pdf_and_add_signatures, get_page_count
from app.services.llm_service import detect_signatures_on_page
from app.models import SignatureLocation

st.set_page_config(page_title="AI PDF Signer", layout="wide")

st.title("✍️ AI-Powered PDF Signature Placer")
st.markdown("Upload a PDF to automatically detect and place signature fields.")

# checking API Key
if "GEMINI_API_KEY" not in os.environ:
    st.error("❌ GEMINI_API_KEY not found in environment variables.")
    st.info("If running locally, set it in your terminal. If on Render, add it to Environment Variables.")
    st.stop()

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Save to temp file strictly for PyMuPDF if needed, or just read bytes
    pdf_bytes = uploaded_file.read()
    
    st.sidebar.header("Document Info")
    page_count = get_page_count(pdf_bytes)
    st.sidebar.write(f"**Pages:** {page_count}")
    
    if st.button("Process PDF"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        all_signatures = []
        
        for i in range(1, page_count + 1):
            status_text.text(f"Processing page {i}/{page_count}...")
            
            # Render page
            img_bytes = render_page_to_image(pdf_bytes, i)
            if img_bytes:
                # Detect
                signatures = detect_signatures_on_page(img_bytes, i)
                if signatures:
                    st.toast(f"Found {len(signatures)} signatures on page {i}!")
                    all_signatures.extend(signatures)
            
            progress_bar.progress(i / page_count)
            
        progress_bar.empty()
        status_text.text("Processing complete!")
        
        if not all_signatures:
            st.warning("No signature lines detected.")
        else:
            st.success(f"Detected {len(all_signatures)} signature fields in total.")
            
            # Create Processed PDF
            signed_pdf_bytes = process_pdf_and_add_signatures(pdf_bytes, all_signatures)
            
            # Download Button
            st.download_button(
                label="⬇️ Download Signed PDF",
                data=signed_pdf_bytes,
                file_name=f"signed_{uploaded_file.name}",
                mime="application/pdf"
            )
            
            # Preview (Optional: Show debug info)
            with st.expander("Detailed Detection Results"):
                for sig in all_signatures:
                    st.json(sig.model_dump())
