from pydantic import BaseModel
from typing import Literal, List, Optional, Dict, Any
from core.system.formats.a2a_part import Part

class Message(BaseModel):
    role: Literal["user", "agent"]
    parts: List[Part]
    metadata: Optional[Dict[str, Any]] = None
