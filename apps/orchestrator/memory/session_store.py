from typing import Dict, List, Optional
from core.system.formats.a2a import Task

class SessionMemory:
    """
    context_id 단위로 오케스트레이터가 기억할 세션 기반 메모리
    """
    _sessions: Dict[str, List[Task]] = {}

    @classmethod
    def save_task(cls, context_id: str, task: Task):
        cls._sessions.setdefault(context_id, []).append(task)
        print(f"🧠 [SessionMemory] Task 저장됨: {task.id} → context: {context_id}")

    @classmethod
    def get_tasks(cls, context_id: str) -> List[Task]:
        return cls._sessions.get(context_id, [])

    @classmethod
    def get_last_task(cls, context_id: str) -> Optional[Task]:
        tasks = cls.get_tasks(context_id)
        return tasks[-1] if tasks else None
