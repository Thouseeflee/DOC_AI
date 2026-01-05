import json
import os
import io
import PIL.Image
from google import genai
from google.genai import types
from app.models import SignatureLocation, BoundingBox
from typing import List

# Client is initialized per request or globally if key is constant.
# We'll initialize lazily to avoid immediate errors if env var is missing.

def detect_signatures_on_page(image_bytes: bytes, page_num: int) -> List[SignatureLocation]:
    """
    Sends the PDF page image to Google Gemini to detect signature lines.
    Returns a list of SignatureLocation objects.
    """
    if "GEMINI_API_KEY" not in os.environ:
        print("GEMINI_API_KEY not found in environment variables.")
        return []

    try:
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        
        prompt = """
        You are an expert document analyzer detecting signature boxes.
        Analyze this image of a document page.
        Identify all locations where a signature is required. Typically these are lines with labels like "Signature", "Signed by", "Name", or explicit boxes.
        
        For each signature field found, return a JSON object with:
        - "signer_name": The name or title of the signer (e.g., "John Doe", "Tenant", "Landlord"). If unknown, use the label.
        - "role": The role of the signer (e.g., "Party A", "Manager").
        - "bounding_box": The coordinates of the signature area in the format [ymin, xmin, ymax, xmax] on a scale of 0 to 1000.
          - ymin: Top edge relative to image height
          - xmin: Left edge relative to image width
          - ymax: Bottom edge relative to image height
          - xmax: Right edge relative to image width
        
        The bounding box should cover the space where the signature should be placed, usually just above the line or inside the box.
        Do NOT include the text label in the box if possible, just the empty space for signing.
        
        Return ONLY valid JSON in the format:
        {
            "signatures": [
                { "signer_name": "...", "role": "...", "bounding_box": [ymin, xmin, ymax, xmax] }
            ]
        }
        """

        # Convert bytes to PIL Image
        image = PIL.Image.open(io.BytesIO(image_bytes))

        # Using standard model name 'gemini-1.5-flash'. 
        # The new SDK normally maps this correctly to the available version.
        response = client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                response_mime_type='application/json'
            )
        )
        
        content = response.text
        data = json.loads(content)
        
        results = []
        for sig in data.get("signatures", []):
            bbox = sig["bounding_box"]
            results.append(SignatureLocation(
                signer_name=sig.get("signer_name", "Unknown"),
                role=sig.get("role", "Signer"),
                bounding_box=BoundingBox(
                    ymin=int(bbox[0]),
                    xmin=int(bbox[1]),
                    ymax=int(bbox[2]),
                    xmax=int(bbox[3])
                ),
                page_number=page_num
            ))
            
        return results

    except Exception as e:
        print(f"Error calling Gemini LLM: {e}")
        return []
