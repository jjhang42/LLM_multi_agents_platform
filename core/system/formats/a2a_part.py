from pydantic import BaseModel, Field, HttpUrl, root_validator
from typing import Optional, Literal, Dict, Any, Union


# --- TextPart ---
class TextPart(BaseModel):
    type: Literal["text"]
    text: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


# --- FilePart ---
class FilePayload(BaseModel):
    name: Optional[str] = None
    mimeType: Optional[str] = None
    bytes: Optional[str] = None  # base64 encoded
    uri: Optional[str] = None    # file URL

    @root_validator
    def validate_content(cls, values):
        if not values.get("bytes") and not values.get("uri"):
            raise ValueError("Either 'bytes' or 'uri' must be provided in file")
        return values


class FilePart(BaseModel):
    type: Literal["file"]
    file: FilePayload
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


# --- DataPart ---
class DataPart(BaseModel):
    type: Literal["data"]
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

# --- Union Part ---
Part = Union[TextPart, FilePart, DataPart]
