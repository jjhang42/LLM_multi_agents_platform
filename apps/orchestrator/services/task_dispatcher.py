from core.system.formats.a2a import TaskSendParams, Task, TaskStatus, TaskState, Message
from core.system.formats.trace_log import TraceLog
from apps.orchestrator.broker_client import get_broker
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from datetime import datetime, timezone

async def dispatch_task(task_data: TaskSendParams):
    broker = get_broker()

    now = datetime.now(timezone.utc)

    task = Task(
        id=task_data.id,
        session_id=task_data.session_id or f"session-{task_data.id}",
        status=TaskStatus(
            state=TaskState.SUBMITTED,
            message=task_data.message,
            timestamp=now
        ),
        history=[task_data.message],
        metadata=task_data.metadata
    )

    trace = TraceLog(
        event_type="task_sent",
        source="orchestrator",
        target="agent_core",
        task_id=task.id,
        session_id=task.session_id,
        payload={"task_type": task_data.message.parts[0].type}
    )

    await broker.send("agent_core.task", jsonable_encoder(task.model_dump(exclude_none=True)))
    await broker.send("trace.log", jsonable_encoder(trace.model_dump(exclude_none=True)))

    return JSONResponse(content={
        "status": "dispatched",
        "task_id": task.id,
        "timestamp": now.isoformat()
    })
