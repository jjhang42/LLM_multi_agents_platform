import os
from core.adapters.executor.gemini_executor_adapter import GeminiExecutorAdapter
from core.adapters.executor.openai_executor_adapter import OpenAIExecutorAdapter
from core.adapters.executor.claude_executor_adapter import ClaudeExecutorAdapter
from core.adapters.executor.llm_executor_base import LLMExecutorBase

EXECUTORS = {
    "gemini": GeminiExecutorAdapter,
    "openai": OpenAIExecutorAdapter,
    "claude": ClaudeExecutorAdapter,
}

def get_executor(model: str = None) -> LLMExecutorBase:
    """
    모델 이름에 따라 ExecutorAdapter 인스턴스를 반환합니다.
    기본값은 .env 설정 (없으면 gemini).
    """
    model_name = model or os.getenv("DEFAULT_EXECUTOR_PROVIDER", "gemini")
    model_name = model_name.lower()

    adapter_class = EXECUTORS.get(model_name)
    if not adapter_class:
        raise ValueError(f"Unsupported executor model: {model_name}")

    return adapter_class()

# 사용 예시
# executor = get_executor("openai")
# result = await executor.run(task)
