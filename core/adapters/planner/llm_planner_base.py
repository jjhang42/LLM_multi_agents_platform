from abc import ABC, abstractmethod
from typing import Dict, Tuple
from core.system.metadata.task_graph import TaskGraph

class LLMPlannerBase(ABC):
    @abstractmethod
    async def parse(self, input_text: str) -> Tuple[Dict[str, dict], TaskGraph]:
        """자연어 → 여러 Task들과 그 관계(TaskGraph) 반환"""
        pass

    @abstractmethod
    async def generate_natural_language(self, task: dict) -> str:
        """Task를 자연어로 변환"""
        pass
