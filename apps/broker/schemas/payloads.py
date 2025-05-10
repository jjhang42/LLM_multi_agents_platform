from pydantic import BaseModel
from typing import Dict, List
from core.system.formats.a2a import Task


class GraphField(BaseModel):
    dependencies: Dict[str, List[str]]
    completed: List[str] = []


class TaskGraphPayload(BaseModel):
    context_id: str
    tasks: Dict[str, Task]
    graph: GraphField


class TaskSendResult(BaseModel):
    status: str = "broker_received"
    context_id: str
    message: str
