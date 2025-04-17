from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


# 1. A2A 표준 Task 상태
class TaskState(str, Enum):
    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    CANCELED = "canceled"
    FAILED = "failed"
    UNKNOWN = "unknown"


# 2. TaskStatus 구조 (상태 + 메시지 + 타임스탬프)
class TaskStatus(BaseModel):
    state: TaskState
    message: Optional["Message"] = None  # Message는 message.py에서 정의 예정
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


# 3. 메인 Task 객체
class Task(BaseModel):
    id: str                                 # 고유 Task ID
    session_id: str                         # 클라이언트가 정의한 세션 ID
    status: TaskStatus                      # 현재 상태
    history: Optional[List["Message"]] = None  # 이전 메시지 기록 (대화 컨텍스트)
    artifacts: Optional[List["Artifact"]] = None  # 결과물 모음
    metadata: Optional[Dict[str, Any]] = None     # 커스텀 메타데이터
        

# 4. SSE 기반 상태 업데이트 이벤트
class TaskStatusUpdateEvent(BaseModel):
    id: str                         # Task ID
    status: TaskStatus              # 새로운 상태
    final: bool                     # 상태 스트리밍의 종료 여부
    metadata: Optional[Dict[str, Any]] = None


# 5. SSE 기반 아티팩트 업데이트 이벤트
class TaskArtifactUpdateEvent(BaseModel):
    id: str
    artifact: "Artifact"           # 신규 생성된 결과물
    metadata: Optional[Dict[str, Any]] = None


# 6. 클라이언트 → 에이전트 요청 시 사용
class TaskSendParams(BaseModel):
    id: str
    session_id: Optional[str] = None
    message: "Message"
    history_length: Optional[int] = None
    push_notification: Optional["PushNotificationConfig"] = None
    metadata: Optional[Dict[str, Any]] = None
