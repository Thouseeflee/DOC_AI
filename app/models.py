from pydantic import BaseModel
from typing import List, Optional

class BoundingBox(BaseModel):
    ymin: int
    xmin: int
    ymax: int
    xmax: int

class SignatureLocation(BaseModel):
    signer_name: str
    role: str
    bounding_box: BoundingBox
    page_number: int  # 1-indexed

class DetectResponse(BaseModel):
    signatures: List[SignatureLocation]
