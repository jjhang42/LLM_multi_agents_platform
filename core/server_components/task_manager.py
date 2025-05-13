# apps/agent_creator/in_memory_task_manager.py

from core.system.formats.a2a import TaskSendParams
from typing import Dict
import asyncio

class InMemoryTaskManager:
    def __init__(self):
        self.tasks: Dict[str, TaskSendParams] = {}
        self.lock = asyncio.Lock()

    async def upsert_task(self, params: TaskSendParams):
        async with self.lock:
            self.tasks[params.id] = params
