import os
import httpx
import mimetypes
from string import Template
from typing import Dict, List
from core.adapters.planner.llm_planner_base import LLMPlannerBase
from core.prompts.loader import load_prompt
from core.system.formats.a2a_part import Part

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

        if self.prompt_parse_task:
            gemini_parts.append({"text": self.prompt_parse_task.strip()})

        for part in parts:
            if part.type == "text":
                gemini_parts.append({"text": part.text})

            elif part.type in {"image_url", "file_url", "pdf_url", "txt_url"} or part.type.startswith("file_url"):
                mime_type = infer_mime_type_from_url(part.url)

                gemini_parts.append({
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": part.url
                    }
                })

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

        return data["candidates"][0]["content"]["parts"][0]["text"]

    async def _call_llm(self, input_text: str) -> str:
        prompt = Template(self.prompt_parse_task).substitute(input_text=input_text)
        return await self._query_gemini(prompt)

    async def _query_gemini(self, prompt: str) -> str:
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        url = f"{self.api_base}/{self.model}:generateContent?key={self.api_key}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]

    async def generate_natural_language(self, task: dict) -> str:
        task_text = str(task)
        prompt = Template(self.prompt_generate_nl).substitute(task_text=task_text)
        return await self._query_gemini(prompt)
