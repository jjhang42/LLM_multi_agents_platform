from typing import Dict, List, Optional

class TaskGraph:
    def __init__(self):
        self.dependencies: Dict[str, List[str]] = {}
        self.completed: set = set()

    def add_task(self, task_id: str, depends_on: Optional[List[str]] = None):
        self.dependencies[task_id] = depends_on or []

    def mark_completed(self, task_id: str):
        self.completed.add(task_id)

    def get_ready_tasks(self) -> List[str]:
        ready = []
        for task_id, deps in self.dependencies.items():
            if task_id in self.completed:
                continue
            if all(dep in self.completed for dep in deps):
                ready.append(task_id)
        return ready

    def is_all_completed(self) -> bool:
        return set(self.dependencies.keys()) == self.completed

    def serialize(self) -> dict:
        """TaskGraph를 dict 형태로 직렬화"""
        return {
            "dependencies": self.dependencies,
            "completed": list(self.completed),
        }

    @classmethod
    def deserialize(cls, data: dict) -> "TaskGraph":
        """dict로부터 TaskGraph 복원"""
        graph = cls()
        graph.dependencies = data.get("dependencies", {})
        graph.completed = set(data.get("completed", []))
        return graph
