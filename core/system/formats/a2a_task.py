from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime
from core.system.formats.a2a_message import Message
from core.system.formats.a2a_artifact import Artifact
from core.system.formats.a2a_push import PushNotificationConfig


class TaskState(str, Enum):
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    CANCELED = "canceled"
    FAILED = "failed"
    UNKNOWN = "unknown"

class TaskStatus(BaseModel):
    state: TaskState
    message: Optional[Message] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Task(BaseModel):
    id: str
    session_id: str
    status: TaskStatus
    history: Optional[List[Message]] = None
    artifacts: Optional[List[Artifact]] = None
    metadata: Optional[Dict[str, Any]] = None

class TaskSendParams(BaseModel):
    id: str
    session_id: Optional[str] = None
    message: Message
    history_length: Optional[int] = None
    push_notification: Optional[PushNotificationConfig] = None
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_task(cls, task: Task) -> "TaskSendParams":
        return cls(
            id=task.id,
            session_id=task.session_id,
            message=task.status.message or Message(role="user", content="", timestamp=datetime.utcnow()),
            metadata=task.metadata or {},
            history_length=len(task.history or [])
        )
