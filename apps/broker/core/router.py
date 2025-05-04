from fastapi.encoders import jsonable_encoder
from core.system.formats.a2a import Task
from core.system.formats.trace_log import TraceLog
from core.system.agent_registry import get_agent_url_from_registry
from core.system.config import get_broker_url
from apps.broker.transport.base import get_transport

# 처리된 task ID를 추적하기 위한 세트
processed_tasks = set()

async def route_task(task: Task):
    # 이미 처리된 task인지 확인
    if task.id in processed_tasks:
        print(f"[Broker] ⚠️ Task {task.id} already processed, skipping")
        return {"status": "skipped", "reason": "already_processed"}
    
    # task ID를 처리된 목록에 추가
    processed_tasks.add(task.id)
    
    transport = get_transport()
    agent_name = task.metadata.get("model", "agent_core")
    target_url = get_agent_url_from_registry(agent_name)

    print(f"\n[Broker] 📦 Routing task '{task.id}'")
    print(f" ├─ To         : {target_url}")
    print(f" ├─ Session ID : {task.session_id}")
    print(f" ├─ State      : {task.status.state}")
    print(f" └─ Metadata   : {task.metadata}")

    # Task 전송 전 trace 로그
    trace_before = TraceLog(
        event_type="task_routing_started",
        source="broker",
        target=agent_name,
        task_id=task.id,
        session_id=task.session_id,
        payload={"task_type": task.status.message.parts[0].type}
    )

    try:
        # Task 전송
        response = await transport.send(target_url, jsonable_encoder(task))
        
        # Task 전송 후 trace 로그
        trace_after = TraceLog(
            event_type="task_routing_completed",
            source="broker",
            target=agent_name,
            task_id=task.id,
            session_id=task.session_id,
            payload={
                "task_type": task.status.message.parts[0].type,
                "status_code": response.status_code
            }
        )
        
        # Trace 로그 전송
        await transport.send(get_broker_url("trace"), jsonable_encoder(trace_before))
        await transport.send(get_broker_url("trace"), jsonable_encoder(trace_after))
        
        return {"status": "routed", "to": agent_name}
    except Exception as e:
        print(f"[Broker] ❌ Routing error → {e}")
        # 에러 발생 시 trace 로그
        trace_error = TraceLog(
            event_type="task_routing_failed",
            source="broker",
            target=agent_name,
            task_id=task.id,
            session_id=task.session_id,
            payload={
                "error": str(e),
                "task_type": task.status.message.parts[0].type
            }
        )
        await transport.send(get_broker_url("trace"), jsonable_encoder(trace_error))
        raise
