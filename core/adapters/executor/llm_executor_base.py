# core/adapters/executor/llm_executor_base.py
from abc import ABC, abstractmethod
from typing import Any

class LLMExecutorBase(ABC):
    @abstractmethod
    async def run(self, task: dict) -> Any:
        """Task를 받아 실행하고 결과를 반환"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """어댑터 이름을 반환"""
        pass
