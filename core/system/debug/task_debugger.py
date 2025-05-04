# core/system/debug/task_debugger.py

from typing import Any, Dict
from core.system.metadata.task_graph import TaskGraph
from core.system.formats.a2a import Task

def debug_print_loose_tasks_and_graph(tasks: Dict[str, Any], graph: TaskGraph) -> None:
    print("\n🧩 Loose Task 목록:")
    for task_id, task in tasks.items():
        print(f"- ID: {task_id}")

        # dict 또는 Pydantic 모델 방어 처리
        if isinstance(task, dict):
            task_data = task
        elif hasattr(task, "model_dump"):  # Pydantic v2
            task_data = task.model_dump()
        else:
            task_data = task.__dict__

        metadata = task_data.get("metadata", {})

        print(f"  Type: {metadata.get('type', 'N/A')}")
        print(f"  Action: {metadata.get('action', 'N/A')}")
        print(f"  Target: {metadata.get('target', 'N/A')}")
        print(f"  Depends: {metadata.get('depends', [])}")
        print(f"  Status: {task_data.get('status')}")
        print()

    print("🔗 Graph Dependencies:")
    for task_id, deps in graph.dependencies.items():
        print(f"- {task_id} ← {deps}")

def debug_print_a2a_tasks_and_graph(tasks: Dict[str, Task], graph: TaskGraph) -> None:
    print("\n🧩 A2A Task 목록:")
    for task_id, task in tasks.items():
        metadata = task.metadata or {}

        print(f"- ID: {task.id}")
        print(f"  Session: {task.session_id}")
        print(f"  Type: {metadata.get('type', 'N/A')}")
        print(f"  Action: {metadata.get('action', 'N/A')}")
        print(f"  Target: {metadata.get('target', 'N/A')}")
        print(f"  Depends: {metadata.get('depends', [])}")
        print(f"  State: {task.status.state}")
        print()

    print("🔗 Graph Dependencies:")
    for task_id, deps in graph.dependencies.items():
        print(f"- {task_id} ← {deps}")
