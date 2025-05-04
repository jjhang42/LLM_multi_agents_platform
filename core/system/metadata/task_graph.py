from typing import Dict, List, Optional, Set


class TaskGraph:
    def __init__(self):
        self.dependencies: Dict[str, List[str]] = {}
        self.completed: Set[str] = set()

    def add_task(self, task_id: str, depends_on: Optional[List[str]] = None):
        """태스크를 그래프에 추가하고, 종속성이 존재하지 않으면 경고"""
        depends_on = depends_on or []
        self.dependencies[task_id] = depends_on

        for dep in depends_on:
            if dep not in self.dependencies:
                print(f"[Warning] '{task_id}' depends on undefined task '{dep}'")

    def has_cycle(self) -> bool:
        """사이클(DAG 위반) 존재 여부를 반환"""
        visited = set()
        path = set()

        def visit(node: str) -> bool:
            if node in path:
                return True  # 사이클 감지
            if node in visited:
                return False
            path.add(node)
            for neighbor in self.dependencies.get(node, []):
                if visit(neighbor):
                    return True
            path.remove(node)
            visited.add(node)
            return False

        return any(visit(node) for node in self.dependencies)

    def mark_completed(self, task_id: str):
        self.completed.add(task_id)

    def get_ready_tasks(self) -> List[str]:
        """모든 의존 태스크가 완료된 실행 가능 태스크 반환"""
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
        """TaskGraph를 직렬화된 딕셔너리로 반환"""
        return {
            "dependencies": self.dependencies,
            "completed": list(self.completed),
        }

    @classmethod
    def deserialize(cls, data: dict) -> "TaskGraph":
        """직렬화된 딕셔너리로부터 TaskGraph 복원"""
        graph = cls()
        graph.dependencies = data.get("dependencies", {})
        graph.completed = set(data.get("completed", []))
        return graph
