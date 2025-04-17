from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any
from datetime import datetime


class TraceLog(BaseModel):
    event_type: Literal[
        "task_sent",
        "task_received",
        "result_sent",
        "result_received",
        "agent_delegated",
        "error_occurred"
    ]
    source: str                           # sender agent ID
    target: Optional[str] = None          # receiver agent ID
    task_id: str
    session_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: Optional[Dict[str, Any]] = None  # 선택적 원본 or 요약
