from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any, List
from uuid import uuid4
from datetime import datetime

class TaskMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    sender: str  # who sent this task (e.g. "orchestrator")
    receiver: str  # target agent name
    task_type: Literal["summarize", "translate", "search", "generate", "custom"]
    payload: Dict[str, Any]  # the input data for the task
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TaskResult(BaseModel):
    task_id: str
    receiver: str  # agent name that responded
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    finished_at: datetime = Field(default_factory=datetime.utcnow)

class AgentStatus(BaseModel):
    agent_id: str
    agent_type: Literal["llm", "tool", "func", "react"]
    is_alive: bool
    last_heartbeat: datetime = Field(default_factory=datetime.utcnow)

class RoutingCommand(BaseModel):
    from_: str = Field(..., alias="from")
    to: str
    route_type: Literal["broadcast", "direct"]
    topic: str
    message: Dict[str, Any]
