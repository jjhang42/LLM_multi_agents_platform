import uuid
import httpx
from typing import Dict, Any
from core.adapters.planner.planner_router import get_planner
from apps.orchestrator.utils.error import handle_exception
from core.system.debug.task_debugger import debug_print_loose_tasks_and_graph
from fastapi.encoders import jsonable_encoder
from core.system.utils.reactflow import taskgraph_to_reactflow
from core.system.memory.agent_card_store import AgentCardStore
from apps.orchestrator.memory.task_history_store import TaskHistoryStore
from core.system.utils.agent_card_utils import group_cards_by_action

def attach_context_id(tasks: Dict[str, Any], context_id: str):
    for task in tasks.values():
        if hasattr(task, "metadata"):
            task.metadata = task.metadata or {}
            task.metadata["context_id"] = context_id
        elif isinstance(task, dict):
            task["metadata"] = task.get("metadata", {})
            task["metadata"]["context_id"] = context_id


def flatten_status(tasks: Dict[str, Any]) -> Dict[str, Any]:
    """status.message를 루트 message로 올려보냄"""
    for task in tasks.values():
        if "status" in task and isinstance(task["status"], dict):
            task["message"] = task["status"].pop("message", None)
    return tasks


def inject_graph_dependencies_into_metadata(tasks: Dict[str, Any], graph) -> None:
    """TaskGraph.dependencies를 각 task.metadata.depends로 삽입"""
    for task_id, depends in graph.dependencies.items():
        if task_id in tasks:
            task = tasks[task_id]
            task.setdefault("metadata", {})
            task["metadata"]["depends"] = depends


async def get_agent_cards_from_broker() -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("http://broker:8000/agents")
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        print(f"❌ 에이전트 카드 로드 실패: {e}")
        return []


async def parse_and_dispatch_task(task_req) -> Dict[str, Any]:
    planner = get_planner()
    context_id = str(uuid.uuid4())

    # ✅ 에이전트 카드 로딩 (메모리 → Fallback to 브로커)
    agent_cards = AgentCardStore.get_all()
    if not agent_cards:
        print("⚠️ [Planner] AgentCardStore 비어 있음 → 브로커에서 재로딩")
        agent_cards = await get_agent_cards_from_broker()
        AgentCardStore.save(group_cards_by_action(agent_cards))

    # ✅ 과거 작업 기록 불러오기
    task_history = TaskHistoryStore.get_last_n(context_id=context_id, limit=10)

    try:
        tasks, graph = await planner.parse(
            parts=task_req.parts,
            agent_cards=agent_cards,
            task_history=task_history,
        )
    except Exception as e:
        return handle_exception("planner", e)

    attach_context_id(tasks, context_id)
    debug_print_loose_tasks_and_graph(tasks, graph)

    if set(tasks.keys()) == {"chat_response"}:
        return {
            "context_id": context_id,
            "type": "chat",
            "message": jsonable_encoder(tasks["chat_response"].status.message)
        }

    encoded_tasks = jsonable_encoder(tasks)
    flatten_status(encoded_tasks)
    inject_graph_dependencies_into_metadata(encoded_tasks, graph)

    payload = {
        "context_id": context_id,
        "tasks": encoded_tasks,
        "graph": graph.dependencies,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("http://broker:8000/tasks", json=payload)
        if response.status_code == 200:
            print(f"[Orchestrator] ✅ Broker received task request successfully.")
        else:
            print(f"[Orchestrator] ❌ Broker error: {response.status_code} {response.text}")
    except Exception as e:
        return handle_exception("broker", e)

    return {
        "context_id": context_id,
        "type": "task_graph",
        "flow": taskgraph_to_reactflow(graph, tasks),
        "tasks": jsonable_encoder(tasks),
        "graph": graph.dependencies
    }
