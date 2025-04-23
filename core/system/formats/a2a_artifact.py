from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from core.system.formats.a2a_part import Part


class Artifact(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parts: List[Part]
    metadata: Optional[Dict[str, Any]] = None
    index: int
    append: Optional[bool] = None
    last_chunk: Optional[bool] = None
