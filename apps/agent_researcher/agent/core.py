import logging
from typing import Optional, Any, AsyncIterable, Dict
from uuid import uuid4

from crewai import Agent, Crew, LLM, Task
from crewai.process import Process
from core.server_components.cache.in_memory_cache import InMemoryCache
from core.system.formats.research_data import ResearchData

logger = logging.getLogger(__name__)


class ResearchAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain", "text/markdown"]

    def __init__(self):
        self.model = LLM(model="gemini/gemini-2.0-pro")

        self.research_agent = Agent(
            role="Research Analyst",
            goal="Gather relevant web information and summarize key insights.",
            backstory="You are an expert in web-based research and content summarization.",
            verbose=True,
            allow_delegation=False,
            tools=[],  # 향후: 웹 검색 툴 삽입 가능
            llm=self.model,
        )

        self.research_task = Task(
            description=(
                "Based on the user query: '{user_prompt}', "
                "perform research and generate a markdown summary. "
                "Highlight key points, sources, and findings clearly."
            ),
            expected_output="A well-structured markdown summary.",
            agent=self.research_agent,
        )

        self.crew = Crew(
            agents=[self.research_agent],
            tasks=[self.research_task],
            process=Process.sequential,
            verbose=False,
        )

    def invoke(self, query: str, session_id: str) -> Optional[str]:
        """쿼리 실행 및 캐시 저장 후 ID 반환"""
        summary_id = uuid4().hex
        logger.info(f"[ResearchAgent] Running query. session={session_id}, summary_id={summary_id}")

        result_text = self.crew.kickoff({
            "user_prompt": query,
            "session_id": session_id,
        })

        cache = InMemoryCache()
        session_data = cache.get(session_id) or {}
        session_data[summary_id] = ResearchData(
            id=summary_id,
            text=result_text,
            mime_type="text/markdown",
        )
        cache.set(session_id, session_data)
        return summary_id

    def get_summary_data(self, session_id: str, summary_id: str) -> ResearchData:
        """저장된 요약 결과를 반환"""
        cache = InMemoryCache()
        session_data = cache.get(session_id) or {}
        return session_data.get(summary_id) or ResearchData(error="Summary not found.")

    async def stream(self, query: str) -> AsyncIterable[Dict[str, Any]]:
        raise NotImplementedError("Streaming not supported.")
