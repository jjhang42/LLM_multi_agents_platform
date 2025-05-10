import uuid
import httpx
from typing import Dict, Any
from core.adapters.planner.planner_router import get_planner
from core.system.utils.serialize import serialize
from apps.orchestrator.utils.error import handle_exception
from core.system.debug.task_debugger import debug_print_loose_tasks_and_graph
from fastapi.encoders import jsonable_encoder
from core.system.utils.reactflow import taskgraph_to_reactflow

def attach_context_id(tasks: Dict[str, Any], context_id: str):
    for task in tasks.values():
        if hasattr(task, "metadata"):
            task.metadata = task.metadata or {}
            task.metadata["context_id"] = context_id
        elif isinstance(task, dict):
            task["context_id"] = context_id


async def parse_and_dispatch_task(task_req) -> Dict[str, Any]:
    planner = get_planner()

    try:
        tasks, graph = await planner.parse(task_req.parts)
    except Exception as e:
        return handle_exception("planner", e)

    context_id = str(uuid.uuid4())
    attach_context_id(tasks, context_id)

    debug_print_loose_tasks_and_graph(tasks, graph)

    # ✅ 일반 채팅 감지 시 broker 전송 없이 반환
    if set(tasks.keys()) == {"chat_response"}:
        print("[Orchestrator] General chat response detected. Returned directly without broker forwarding.")
        return {
            "context_id": context_id,
            "type": "chat",
            "message": jsonable_encoder(tasks["chat_response"].status.message)
        }

    # ✅ broker 전송용 직렬화
    payload = serialize({
        "context_id": context_id,
        "tasks": tasks,
        "graph": graph.serialize(),
    })

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("http://broker:8000/tasks", json=payload)
        if response.status_code == 200:
            print(f"Broker received task request: {response.status_code}")
    except Exception as e:
        return handle_exception("broker", e)

    # ✅ 프론트엔드에 시각화 데이터도 전달
    return {
        "context_id": context_id,
        "type": "task_graph",
        "flow": taskgraph_to_reactflow(graph, tasks),
        "tasks": jsonable_encoder(tasks),
        # "graph": graph.to_edge_list()
        "graph": graph.serialize()
    }
