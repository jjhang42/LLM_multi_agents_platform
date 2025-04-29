# core/system/parsers/task_assembler.py

from typing import Dict, Any, Tuple
import uuid
from core.system.metadata.task_graph import TaskGraph

def assemble_tasks_with_graph(raw_tasks: Any) -> Tuple[Dict[str, Any], TaskGraph]:
    """
    LLM이 반환한 raw task들을 A2A 포맷 + TaskGraph로 정리합니다.
    Args:
        raw_tasks (Any): LLM 파싱 결과 (list 또는 dict)
    Returns:
        Tuple[Dict[str, Any], TaskGraph]: 표준화된 tasks, graph
    """
    assembled = {}
    graph = TaskGraph()

    # raw_tasks가 리스트면 복수 task, dict면 단일 task
    if isinstance(raw_tasks, dict):
        raw_tasks = [raw_tasks]

    for task in raw_tasks:
        real_id = task.get("id") or f"task_{uuid.uuid4().hex[:8]}"
        
        assembled_task = {
            "id": real_id,
            "type": task.get("type", "action"),
            "parameters": task.get("parameters", {}),
            "depends": task.get("depends", []),
            "status": task.get("status", "pending"),
            "result": task.get("result", None),
            "metadata": task.get("metadata", {})
        }

        assembled[real_id] = assembled_task
        graph.add_task(real_id, assembled_task["depends"])

    return assembled, graph
