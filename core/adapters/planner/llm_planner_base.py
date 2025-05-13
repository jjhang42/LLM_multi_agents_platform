from abc import ABC, abstractmethod
from typing import Dict, Tuple, List, Literal, Any
from core.system.metadata.task_graph import TaskGraph
from core.system.parser.task_assembler import assemble_tasks_with_graph
from core.system.utils.llm_response_parser import llm_response_parser
from core.system.formats.a2a import Task
from core.system.formats.a2a_part import Part
import traceback
import json


class LLMPlannerBase(ABC):
    async def parse(
        self,
        parts: List[Part],
        agent_cards: List[Dict] = [],
        task_history: List[Task] = []
    ) -> Tuple[Dict[str, Task], TaskGraph]:
        """
        입력 유형(chat, planning, task)에 따라 다른 경로로 Task + Graph를 생성합니다.
        """
        input_type = self._classify_input_type(parts)
        print(f"🔎 [Planner] Input type classified as: {input_type}")

        if input_type == "chat":
            task = await self._chat_response(parts)
            return {"chat_response": task}, TaskGraph()

        elif input_type == "task":
            return self._parse_task_json_direct(parts)

        else:  # planning
            return await self._run_llm_planning(parts, agent_cards, task_history)

    def _classify_input_type(self, parts: List[Part]) -> Literal["chat", "planning", "task"]:
        text = next((p.text for p in parts if p.type == "text"), "")
        if text.strip().startswith("{") and '"tasks"' in text:
            return "task"
        elif any(kw in text for kw in ["검색", "요약", "정리", "설명", "이미지", "날씨"]):
            return "planning"
        return "chat"

    async def _run_llm_planning(
        self,
        parts: List[Part],
        agent_cards: List[Dict],
        task_history: List[Task]
    ) -> Tuple[Dict[str, Task], TaskGraph]:
        """
        LLM에 context를 포함한 프롬프트를 전달하고 결과를 파싱합니다.
        최대 2회 재시도하며, DAG 검증 포함.
        """
        user_input = next((p.text for p in parts if getattr(p, "type", None) == "text"), "")
        for attempt in range(2):
            try:
                llm_context = {
                    "parts": parts,
                    "agent_cards": agent_cards,
                    "prior_tasks": [t.dict() for t in task_history]
                }

                raw_response = await self._call_llm_with_parts(llm_context)
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

    def _parse_task_json_direct(self, parts: List[Part]) -> Tuple[Dict[str, Task], TaskGraph]:
        """
        JSON 형태로 직접 task 입력이 들어온 경우 파싱 처리
        """
        try:
            raw_json = next((p.text for p in parts if p.type == "text"), "{}")
            data = json.loads(raw_json)
            tasks, graph = assemble_tasks_with_graph(data["tasks"], data.get("graph"))
            return tasks, graph
        except Exception as e:
            raise RuntimeError(f"❌ 직접 입력된 JSON 파싱 실패: {e}")

    @abstractmethod
    async def _call_llm_with_parts(self, context: Dict[str, Any]) -> str:
        """
        LLM 호출: parts, agent_cards, prior_tasks를 포함한 context를 prompt로 구성해 호출
        """
        pass

    @abstractmethod
    async def _chat_response(self, parts: List[Part]) -> Task:
        """
        일반적인 단답 응답 처리 (예: chat_response)
        """
        pass

    @abstractmethod
    async def generate_natural_language(self, task: dict) -> str:
        """
        Task를 자연어로 재구성
        """
        pass

    def _parse_response(self, text: str, user_input: str = "") -> List[Task]:
        return llm_response_parser(text, Task, user_input=user_input)
