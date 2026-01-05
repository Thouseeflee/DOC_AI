import fitz  # PyMuPDF
from typing import List
from app.models import SignatureLocation

def process_pdf_and_add_signatures(pdf_bytes: bytes, signatures: List[SignatureLocation]) -> bytes:
    """
    Opens the PDF, adds signature widgets at the specified locations, and returns the modified PDF bytes.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    for sig in signatures:
        # doc is 0-indexed, but our model is 1-indexed
        page_idx = sig.page_number - 1
        if 0 <= page_idx < len(doc):
            page = doc[page_idx]
            page_rect = page.rect
            
            # Convert 0-1000 generic coordinates to PDF Point coordinates
            # LLM: [ymin, xmin, ymax, xmax]
            # PyMuPDF Rect: x0, y0, x1, y1
            
            h = page_rect.height
            w = page_rect.width
            
            # xmin, xmax correspond to width
            x0 = (sig.bounding_box.xmin / 1000.0) * w
            x1 = (sig.bounding_box.xmax / 1000.0) * w
            
            # ymin, ymax correspond to height
            y0 = (sig.bounding_box.ymin / 1000.0) * h
            y1 = (sig.bounding_box.ymax / 1000.0) * h
            
            rect = fitz.Rect(x0, y0, x1, y1)
            
            # Create the widget
            widget = fitz.Widget()
            widget.rect = rect
            widget.field_name = f"Sig_{sig.signer_name.replace(' ', '_')}_{sig.role}"
            
            # Set widget properties to make it look like a signature field
            # PDF_WIDGET_TYPE_SIGNATURE is typically established by setting field flags or type
            # In older PyMuPDF it was complex, but modern versions support field_type.
            # However, explicit constant might vary. 
            # We will default to a text widget that serves as a placeholder if SIGNATURE type fails.
            
            # Try setting it as a Signature widget
            # As of PyMuPDF 1.23+, we can set:
            widget.field_type = fitz.PDF_WIDGET_TYPE_SIGNATURE
            
            # Add the widget to the page
            page.add_widget(widget)
            
    # Save to bytes
    output_bytes = doc.tobytes()
    doc.close()
    return output_bytes

def render_page_to_image(pdf_bytes: bytes, page_num: int) -> bytes:
    """
    Renders a specific page of the PDF to a JPEG image bytes.
    page_num is 1-indexed.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    if 1 <= page_num <= len(doc):
        page = doc[page_num - 1]
        pix = page.get_pixmap(dpi=150) # 150 DPI is usually sufficient for Vision
        img_bytes = pix.tobytes("jpg")
        doc.close()
        return img_bytes
    doc.close()
    return b""

def get_page_count(pdf_bytes: bytes) -> int:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    count = len(doc)
    doc.close()
    return count
