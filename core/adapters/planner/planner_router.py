import os
from core.adapters.planner.gemini_planner_adapter import GeminiPlannerAdapter
from core.adapters.planner.openai_planner_adapter import OpenAIPlannerAdapter
from core.adapters.planner.claude_planner_adapter import ClaudePlannerAdapter
from core.adapters.planner.llm_planner_base import LLMPlannerBase

PLANNERS = {
    "gemini": GeminiPlannerAdapter,
    "openai": OpenAIPlannerAdapter,
    "claude": ClaudePlannerAdapter,
}

def get_planner(model: str = None) -> LLMPlannerBase:
    """
    모델 이름에 따라 PlannerAdapter 인스턴스를 반환합니다.
    기본값은 .env 설정 (없으면 gemini).
    """
    model_name = model or os.getenv("ORCHESTRATOR_LLM_PROVIDER", "gemini")
    model_name = model_name.lower()

    adapter_class = PLANNERS.get(model_name)
    if not adapter_class:
        raise ValueError(f"Unsupported planner model: {model_name}")

    return adapter_class()

# 사용 예시
# planner = get_planner("openai")
# task = await planner.parse_task("회의록을 요약해줘")
