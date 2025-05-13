# core/system/formats/image_data.py
from typing import Optional
from pydantic import BaseModel

class Imagedata(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    mime_type: Optional[str] = None
    bytes: Optional[str] = None
    error: Optional[str] = None
