from typing import Dict, List, Optional, Set, Any
import warnings


class TaskGraph:
    def __init__(self):
        self.dependencies: Dict[str, List[str]] = {}
        self.completed: Set[str] = set()

    def add_task(self, task_id: str, depends_on: Optional[List[str]] = None) -> None:
        """
        태스크를 그래프에 추가합니다.

        Args:
            task_id (str): 태스크 ID
            depends_on (Optional[List[str]]): 의존하는 태스크 ID 목록

        Raises:
            ValueError: 자기 자신을 의존할 경우 예외 발생
        """
        depends_on = depends_on or []

        if task_id in depends_on:
            raise ValueError(f"[TaskGraph] '{task_id}' cannot depend on itself.")

        self.dependencies[task_id] = depends_on

        for dep in depends_on:
            if dep not in self.dependencies:
                warnings.warn(
                    f"[TaskGraph] '{task_id}' depends on undefined task '{dep}'",
                    stacklevel=2
                )

    def has_cycle(self) -> bool:
        """그래프에 순환(Cycle)이 존재하는지 검사합니다."""
        visited: Set[str] = set()
        recursion_stack: Set[str] = set()

        def dfs(node: str) -> bool:
            if node in recursion_stack:
                return True
            if node in visited:
                return False

            visited.add(node)
            recursion_stack.add(node)

            for neighbor in self.dependencies.get(node, []):
                if dfs(neighbor):
                    return True

            recursion_stack.remove(node)
            return False

        return any(dfs(node) for node in self.dependencies)

    def mark_completed(self, task_id: str) -> None:
        """해당 태스크를 완료 상태로 표시합니다."""
        self.completed.add(task_id)

    def get_executable_tasks(self) -> List[str]:
        """
        현재 실행 가능한 태스크 목록을 반환합니다.

        Returns:
            List[str]: 모든 의존 태스크가 완료된 태스크들
        """
        return [
            task_id for task_id, deps in self.dependencies.items()
            if task_id not in self.completed and all(dep in self.completed for dep in deps)
        ]

    def is_all_completed(self) -> bool:
        """모든 태스크가 완료되었는지 확인합니다."""
        return set(self.dependencies.keys()).issubset(self.completed)

    def serialize(self) -> Dict[str, Any]:
        """TaskGraph 객체를 직렬화 가능한 형태로 변환합니다."""
        return {
            "dependencies": self.dependencies,
            "completed": list(self.completed),
        }

    @classmethod
    def deserialize(cls, data: Dict[str, Any]) -> "TaskGraph":
        """직렬화된 딕셔너리에서 TaskGraph 객체를 복원합니다."""
        graph = cls()
        graph.dependencies = {
            str(k): list(v) for k, v in data.get("dependencies", {}).items()
        }
        graph.completed = set(data.get("completed", []))
        return graph

    def to_edge_list(self) -> List[Dict[str, Any]]:
        """
        의존성 정보를 엣지 리스트 형식으로 변환합니다.

        Returns:
            List[Dict[str, Any]]: {"id": task_id, "depends": [dep1, dep2, ...]} 형태의 목록
        """
        return [
            {"id": task_id, "depends": depends}
            for task_id, depends in self.dependencies.items()
        ]

    def __repr__(self):
        return f"<TaskGraph tasks={len(self.dependencies)}, completed={len(self.completed)}>"
