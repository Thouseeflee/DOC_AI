import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response
from typing import List
from app.services.pdf_service import get_page_count, render_page_to_image, process_pdf_and_add_signatures
from app.services.llm_service import detect_signatures_on_page
from app.models import SignatureLocation

app = FastAPI(title="AI PDF Signature Placer")

@app.post("/process-pdf")
async def process_pdf_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    # Read file content
    try:
        contents = await file.read()
    except Exception:
        raise HTTPException(status_code=500, detail="Could not read file")
        
    page_count = get_page_count(contents)
    if page_count == 0:
        raise HTTPException(status_code=400, detail="Empty or invalid PDF")
        
    all_signatures: List[SignatureLocation] = []
    
    # Iterate through pages and detect signatures
    # For a real production app, this should be async/parallelized
    for i in range(1, page_count + 1):
        # Render page to image
        img_bytes = render_page_to_image(contents, i)
        if not img_bytes:
            continue
            
        # Detect signatures on this page
        signatures = detect_signatures_on_page(img_bytes, i)
        all_signatures.extend(signatures)
        
    if not all_signatures:
        # If no signatures found, just return original pdf or a message
        # We will return original for now, maybe with a header
        return Response(content=contents, media_type="application/pdf")
        
    # Place signatures
    processed_pdf = process_pdf_and_add_signatures(contents, all_signatures)
    
    return Response(content=processed_pdf, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=signed_{file.filename}"})

@app.get("/health")
def health_check():
    return {"status": "ok"}
