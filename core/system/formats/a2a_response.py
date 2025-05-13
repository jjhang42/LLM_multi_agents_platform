# core/system/formats/a2a_response.py

from pydantic import BaseModel
from typing import Optional, Any

class TaskSendResult(BaseModel):
    status: str                     # "success", "error" 등
    context_id: Optional[str] = None
    message: Optional[str] = None   # 간단한 응답 설명

class JSONRPCResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[dict] = None