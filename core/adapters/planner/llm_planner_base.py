from abc import ABC, abstractmethod
from typing import Dict, Tuple, List
from core.system.metadata.task_graph import TaskGraph
from core.system.parser.task_assembler import assemble_tasks_with_graph
from core.system.utils.llm_response_parser import llm_response_parser
from core.system.formats.a2a import Task
from core.system.formats.a2a_part import Part
import traceback


class LLMPlannerBase(ABC):
    async def parse(self, parts: List[Part]) -> Tuple[Dict[str, Task], TaskGraph]:
        """
        사용자의 입력을 멀티모달 파트 배열로 받아 LLM 호출 → A2A Task + DAG 그래프 생성
        - DAG 유효성 검사 포함
        - 실패 시 1회 재시도
        """
        user_input = next((p.text for p in parts if getattr(p, "type", None) == "text"), "")

        for attempt in range(2):  # 최대 2회 시도
            try:
                raw_response = await self._call_llm_with_parts(parts)

                parsed_tasks = self._parse_response(raw_response, user_input=user_input)

                tasks, graph = assemble_tasks_with_graph(parsed_tasks)

                if graph.has_cycle():
                    print("❌ Invalid DAG: Cycle detected")
                    if attempt == 0:
                        print("🔁 Retrying...")
                        continue
                    else:
                        raise RuntimeError("DAG Cycle Error: LLM response is repetitive and invalid.")
                return tasks, graph

            except Exception as e:
                print(f"[Planner] Error occurred (attempt {attempt + 1}):", e)
                traceback.print_exc()
                if attempt == 1:
                    raise RuntimeError("LLM parsing or validation failed")

    @abstractmethod
    async def _call_llm_with_parts(self, parts: List[Part]) -> str:
        """
        parts 배열을 LLM-friendly prompt 형식으로 직렬화 후 LLM에 요청.
        실제 모델 API 호출은 하위 클래스에서 구현합니다.
        """
        pass

    def _parse_response(self, text: str, user_input: str = "") -> List[Task]:
        """
        LLM의 JSON 응답 문자열을 Task[]로 파싱.
        - 상태 자동 보완
        - message 필드 추정
        - timestamp 등 시스템 정보 추가
        """
        return llm_response_parser(text, Task, user_input=user_input)

    @abstractmethod
    async def generate_natural_language(self, task: dict) -> str:
        """
        Task 객체를 자연어 문장으로 변환 (요약 등)
        """
        pass
