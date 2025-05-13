from typing import Dict, List, Optional
from core.system.formats.a2a import Task

class TaskHistoryStore:
    """
    오케스트레이터가 과거에 수행된 Task들을 기억하는 메모리 저장소.
    context_id별로 Task 리스트를 저장하며, 복기, 요약, 재실행 등에 활용할 수 있다.
    """

    _history: Dict[str, List[Task]] = {}

    @classmethod
    def save(cls, context_id: str, task: Task):
        """
        특정 context_id에 해당하는 task를 저장합니다.
        """
        cls._history.setdefault(context_id, []).append(task)
        print(f"📚 [TaskHistory] 저장됨: {task.id} (context: {context_id})")

    @classmethod
    def get_last_n(cls, context_id: str, limit: int = 5) -> List[Task]:
        return cls._history.get(context_id, [])[-limit:]

    @classmethod
    def get(cls, context_id: str) -> List[Task]:
        """
        해당 context_id의 전체 Task 리스트를 반환합니다.
        """
        return cls._history.get(context_id, [])

    @classmethod
    def get_last(cls, context_id: str) -> Optional[Task]:
        """
        해당 context_id에서 가장 마지막에 저장된 Task 반환 (없으면 None)
        """
        tasks = cls.get(context_id)
        return tasks[-1] if tasks else None

    @classmethod
    def clear(cls, context_id: str):
        """
        특정 context_id의 task 기록을 삭제합니다.
        """
        if context_id in cls._history:
            del cls._history[context_id]
            print(f"🗑️ [TaskHistory] context {context_id} 기록 삭제됨")

    @classmethod
    def all(cls) -> Dict[str, List[Task]]:
        """
        전체 context_id별 task 기록을 반환합니다.
        """
        return cls._history
