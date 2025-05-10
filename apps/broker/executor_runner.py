from core.adapters.executor.gemini_executor_adapter import GeminiExecutorAdapter
from core.adapters.executor.openai_executor_adapter import OpenAIExecutorAdapter
from core.adapters.executor.claude_executor_adapter import ClaudeExecutorAdapter
from core.adapters.executor.llm_executor_base import LLMExecutorBase
from core.system.formats.a2a import Task
import os

EXECUTORS = {
    "gemini": GeminiExecutorAdapter,
    "openai": OpenAIExecutorAdapter,
    "claude": ClaudeExecutorAdapter,
}

def get_executor(provider: str = None) -> LLMExecutorBase:
    model = (provider or os.getenv("DEFAULT_EXECUTOR_PROVIDER", "gemini")).lower()
    executor_cls = EXECUTORS.get(model)
    if not executor_cls:
        raise ValueError(f"Unsupported model: {model}")
    return executor_cls()

async def execute_task(task: Task) -> str:
    """
    선택된 executor를 통해 task를 실행하고 결과를 반환합니다.
    """
    provider = task.metadata.get("provider", None)
    executor = get_executor(provider)
    result = await executor.run(task)
    return result
