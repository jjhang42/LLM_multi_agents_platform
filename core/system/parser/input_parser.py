from typing import List
from pydantic import BaseModel
from core.system.formats.a2a_part import Part
import mimetypes
from urllib.parse import urlparse

class RawInput(BaseModel):
    text: str
    file_urls: List[str]

def guess_part_type(url: str) -> str:
    """
    URL 확장자를 기반으로 Part 타입 추정
    """
    path = urlparse(url).path
    mime_type, _ = mimetypes.guess_type(path)

    if not mime_type:
        return "file_url"  # 기본값

    main_type = mime_type.split("/")[0]
    sub_type = mime_type.split("/")[1]

    if main_type == "image":
        return "image_url"
    elif main_type == "video":
        return "video_url"
    elif main_type == "audio":
        return "audio_url"
    elif mime_type in ["application/pdf", "text/plain"]:
        return "document_url"
    elif mime_type in ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]:
        return "spreadsheet_url"
    else:
        return "file_url"

def build_parts_from_input(user_input: RawInput) -> List[Part]:
    parts: List[Part] = []

    # ✅ text part
    if user_input.text.strip():
        parts.append(Part(type="text", text=user_input.text.strip()))

    # ✅ file_url part (프론트에서 유효성 검사되었음 가정)
    for url in user_input.file_urls:
        url = url.strip()
        part_type = guess_part_type(url)
        parts.append(Part(type=part_type, url=url))

    return parts
