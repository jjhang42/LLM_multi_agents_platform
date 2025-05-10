import os
import httpx
import mimetypes
import uuid
import json
from string import Template
from typing import List
from core.adapters.planner.llm_planner_base import LLMPlannerBase
from core.prompts.loader import load_prompt
from core.system.formats.a2a_part import Part, TextPart, FilePart


def infer_mime_type_from_url(url: str) -> str:
    mime_type, _ = mimetypes.guess_type(url)
    return mime_type or "application/octet-stream"


class GeminiPlannerAdapter(LLMPlannerBase):
    def __init__(self):
        self.api_key = os.getenv("ORCHESTRATOR_GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
        self.api_base = os.getenv("ORCHESTRATOR_GEMINI_API_BASE", os.getenv("GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta"))
        self.model = os.getenv("ORCHESTRATOR_GEMINI_MODEL", os.getenv("GEMINI_MODEL", "models/gemini-pro"))

        self.prompt_parse_task = load_prompt("planner_parse_task.txt")
        self.prompt_generate_nl = load_prompt("planner_generate_natural_language.txt")

    async def _call_llm_with_parts(self, parts: List[Part]) -> str:
        gemini_parts = []

        # 프롬프트 삽입
        if self.prompt_parse_task:
            gemini_parts.append({"text": self.prompt_parse_task.strip()})

        for part in parts:
            if part.type == "text":
                gemini_parts.append({"text": part.text})

            elif part.type == "file" and isinstance(part, FilePart):
                uri = part.file.uri or ""
                filename = part.file.name or "unnamed"
                gemini_parts.append({"text": f"[첨부파일: {filename}] {uri}"})

            elif hasattr(part, "url"):
                # image_url, pdf_url 등 custom 타입 대응
                gemini_parts.append({"text": f"[파일: {part.type}] {part.url}"})

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": gemini_parts
                }
            ]
        }

        url = f"{self.api_base}/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        # 디버깅용 저장
        if os.getenv("DEBUG_SAVE_LLM_RESPONSE", "false").lower() == "true":
            path = f"/tmp/gemini_response_{uuid.uuid4().hex[:8]}.json"
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Gemini 응답 저장됨: {path}")

        # 안전한 응답 파싱
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"[GeminiPlanner] LLM 응답 파싱 실패: {e}\n전체 응답: {data}")

    async def generate_natural_language(self, task: dict) -> str:
        task_text = str(task)
        prompt = Template(self.prompt_generate_nl).substitute(task_text=task_text)
        return await self.send_gemini_prompt(prompt)

    async def send_gemini_prompt(self, prompt: str) -> str:
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        url = f"{self.api_base}/{self.model}:generateContent?key={self.api_key}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"[GeminiPlanner] 텍스트 응답 파싱 실패: {e}\n전체 응답: {data}")
