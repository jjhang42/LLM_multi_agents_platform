import logging
from typing import Optional, Any, AsyncIterable, Dict

from crewai import Agent, Crew, LLM, Task
from crewai.process import Process

logger = logging.getLogger(__name__)


class MarkdownPublisherAgent:
    SUPPORTED_CONTENT_TYPES = ["text/markdown", "text/plain", "text"]

    def __init__(self):
        self.model = LLM(model="gemini/gemini-2.0-pro")  # 요약 결과에 대한 추가 가공 가능

        self.publisher_agent = Agent(
            role="Markdown Publisher",
            goal="Publish the provided markdown content to an external target (e.g., blog, notion).",
            backstory="You are a publishing assistant that formats and transfers markdown content to external services.",
            verbose=True,
            allow_delegation=False,
            tools=[],  # 향후 Notion API, GitHub Gist 등 연결 가능
            llm=self.model,
        )

        self.publish_task = Task(
            description=(
                "Take the provided markdown content '{user_prompt}' and format it if necessary. "
                "Then simulate publishing to an external target. This is a placeholder agent that could later "
                "integrate with real APIs like Notion or GitHub."
            ),
            expected_output="✅ Simulated publishing confirmation message.",
            agent=self.publisher_agent,
        )

        self.crew = Crew(
            agents=[self.publisher_agent],
            tasks=[self.publish_task],
            process=Process.sequential,
            verbose=False,
        )

    def invoke(self, query: str, session_id: str) -> Optional[str]:
        """
        query: 마크다운 형식의 문자열 (예: 리서처 결과물)
        """
        inputs = {
            "user_prompt": query,
            "session_id": session_id,
        }

        logger.info(f"[MarkdownPublisherAgent] Invoking with inputs: {inputs}")
        return self.crew.kickoff(inputs)

    async def stream(self, query: str) -> AsyncIterable[Dict[str, Any]]:
        raise NotImplementedError("Streaming is not supported by this agent.")
