from fastapi import APIRouter, Request
from core.system.formats.a2a import TaskGraphPayload, TaskSendResult
from broker.core.task_executor import execute_task_graph
from broker.core.executor_runner import ExecutorRunner

router = APIRouter()

@router.post("/tasks", response_model=TaskSendResult)
async def receive_tasks(payload: TaskGraphPayload, request: Request):
    runner: ExecutorRunner = request.app.state.runner
    return await execute_task_graph(payload, runner)
