from typing import Dict, Any, Optional
from core.system.formats.a2a import Task
from core.system.metadata.task_graph import TaskGraph


class BrokerState:
    def __init__(self):
        self.tasks_by_context: Dict[str, Dict[str, Task]] = {}
        self.graphs_by_context: Dict[str, TaskGraph] = {}

    def register(self, context_id: str, tasks: Dict[str, Task], graph_data: Dict[str, Any]) -> str:
        """context_id 기준으로 tasks와 graph를 안전하게 저장"""
        if context_id in self.tasks_by_context:
            print(f"⚠️ Warning: Context ID '{context_id}' already registered. Overwriting.")

        self.tasks_by_context[context_id] = tasks
        self.graphs_by_context[context_id] = TaskGraph.deserialize(graph_data)

        print(f"[Broker] Registered {len(tasks)} tasks with context_id={context_id}")
        return f"{len(tasks)} tasks received and registered."

    def cleanup_if_complete(self, context_id: str) -> None:
        """모든 태스크 완료 시 해당 context 데이터를 메모리에서 제거"""
        graph = self.graphs_by_context.get(context_id)
        if not graph:
            print(f"⚠️ No graph found for context_id={context_id}")
            return

        if graph.is_all_completed():
            print(f"[Broker] ✅ All tasks completed for context_id={context_id}, cleaning up.")
            self.tasks_by_context.pop(context_id, None)
            self.graphs_by_context.pop(context_id, None)

    def get_tasks(self, context_id: str) -> Dict[str, Task]:
        return self.tasks_by_context.get(context_id, {})

    def get_graph(self, context_id: str) -> Optional[TaskGraph]:
        return self.graphs_by_context.get(context_id)
