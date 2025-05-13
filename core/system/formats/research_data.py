from pydantic import BaseModel
from typing import Optional

class ResearchData(BaseModel):
    id: Optional[str] = None
    text: Optional[str] = None
    mime_type: Optional[str] = "text/markdown"
    error: Optional[str] = None
