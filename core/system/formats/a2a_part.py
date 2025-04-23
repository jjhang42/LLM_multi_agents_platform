from pydantic import BaseModel
from typing import Literal, Optional, Dict, Any, Union


class TextPart(BaseModel):
    type: Literal["text"]
    text: str
    metadata: Optional[Dict[str, Any]] = None


class FilePayload(BaseModel):
    name: Optional[str] = None
    mime_type: Optional[str] = None
    bytes: Optional[str] = None  # base64 encoded
    uri: Optional[str] = None

    def get_name_or_default(self):
        return self.name or "unnamed"


class FilePart(BaseModel):
    type: Literal["file"]
    file: FilePayload
    metadata: Optional[Dict[str, Any]] = None


class DataPart(BaseModel):
    type: Literal["data"]
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


Part = Union[TextPart, FilePart, DataPart]
