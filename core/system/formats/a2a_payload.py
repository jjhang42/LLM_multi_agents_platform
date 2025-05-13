from __future__ import annotations
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from core.system.formats.a2a_task import Task, TaskSendParams
from core.system.metadata.task_graph import TaskGraph
from core.system.formats.a2a_message import Message


class TaskGraphPayload(BaseModel):
    """
    복수 Task + TaskGraph를 Broker로 전송할 때 사용하는 전용 직렬화 모델
    """
    context_id: str
    tasks: Dict[str, TaskSendParams]
    graph: Dict[str, List[str]]  # serialized TaskGraph.dependencies

    @classmethod
    def from_task_dict(
        cls,
        context_id: str,
        tasks: Dict[str, Task],
        graph: TaskGraph
    ) -> "TaskGraphPayload":
        return cls(
            context_id=context_id,
            tasks={task_id: TaskSendParams.from_task(task) for task_id, task in tasks.items()},
            graph=graph.serialize()
        )

class SendTaskRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str = "agent.send_task"
    id: Optional[str]
    params: TaskSendParams

class SendTaskResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str]
    result: Any  # 보통 Task 전체

class SendTaskStreamingRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str = "agent.send_task_streaming"
    id: Optional[str]
    params: TaskSendParams

class SendTaskStreamingResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str]
    result: Optional[Any] = None
