from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from .a2a_part import Part


class Artifact(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parts: List[Part]
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    index: int
    append: Optional[bool] = False
    lastChunk: Optional[bool] = True
