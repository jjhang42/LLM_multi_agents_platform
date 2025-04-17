from pydantic import BaseModel, Field
from typing import Literal, List, Optional, Dict, Any
from .a2a_part import Part


class Message(BaseModel):
    role: Literal["user", "agent"]
    parts: List[Part]
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
