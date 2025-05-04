from abc import ABC, abstractmethod
from typing import Dict, Tuple, List, Literal
from core.system.metadata.task_graph import TaskGraph
from core.system.parser.task_assembler import assemble_tasks_with_graph
from core.system.utils.llm_response_parser import llm_response_parser
from core.system.formats.a2a import Task
from core.system.formats.a2a_part import Part

class LLMPlannerBase(ABC):
    async def parse(self, parts: List[Part]) -> Tuple[Dict[str, Task], TaskGraph]:
        """
        사용자의 입력을 멀티모달 파트 배열로 받아 LLM 호출 및 A2A Task + Graph를 반환합니다.
        예: [{"type": "text", "text": "이미지를 설명해줘"}, {"type": "image_url", "url": "https://..."}]
        """
        raw = await self._call_llm_with_parts(parts)
        print("[DEBUG] Raw LLM Output:", raw)

        # 텍스트로 구성된 첫 번째 질문만 추출 (입력 메시지 보완용)
        text_prompt = next((p.text for p in parts if p.type == "text"), "")
        parsed_tasks = self._parse_response(raw, text_prompt)
        print("[DEBUG] Planner Parser result: ", parsed_tasks)

        return assemble_tasks_with_graph(parsed_tasks)

    @abstractmethod
    async def _call_llm_with_parts(self, parts: List[Part]) -> str:
        """
        멀티모달 파트 배열을 기반으로 LLM 호출 수행.
        구현체에서는 이를 LLM 형식 (예: Gemini JSON) 에 맞게 직렬화하여 요청해야 합니다.
        """
        pass

    def _parse_response(self, text: str, user_input: str) -> list[Task]:
        """
        LLM에서 반환된 JSON 문자열을 A2A Task 객체 리스트로 파싱.
        상태 필드, 타임스탬프, 메시지 자동 보완.
        """
        return llm_response_parser(text, Task, user_input=user_input)

    @abstractmethod
    async def generate_natural_language(self, task: dict) -> str:
        """
        A2A Task → 자연어로 변환 (요약, 히스토리 등)
        """
        pass
