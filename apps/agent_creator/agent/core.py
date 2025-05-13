import re
import logging
from typing import Optional, Any, AsyncIterable, Dict

from crewai import Agent, Crew, LLM, Task
from crewai.process import Process

from core.agent_tools.image_tool import generate_image_tool
from core.server_components.cache.in_memory_cache import InMemoryCache
from core.system.formats.image_data import Imagedata

logger = logging.getLogger(__name__)


class ImageGenerationAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain", "image/png"]

    def __init__(self):
        self.model = LLM(model="gemini/gemini-2.0-flash")

        self.image_creator_agent = Agent(
            role="Image Creation Expert",
            goal="Generate an image based on the user's text prompt.",
            backstory="You are a digital artist powered by AI.",
            verbose=False,
            allow_delegation=False,
            tools=[generate_image_tool],
            llm=self.model,
        )

        self.image_creation_task = Task(
            description=(
                "Receive a user prompt: '{user_prompt}'. "
                "Rewrite if needed for clarity and call ImageGenerationTool using: "
                "{user_prompt}, {session_id}, and optionally {artifact_file_id}."
            ),
            expected_output="The ID of the generated image.",
            agent=self.image_creator_agent,
        )

        self.image_crew = Crew(
            agents=[self.image_creator_agent],
            tasks=[self.image_creation_task],
            process=Process.sequential,
            verbose=False,
        )

    def invoke(self, query: str, session_id: str) -> Optional[str]:
        artifact_file_id = self._extract_artifact_file_id(query)

        inputs = {
            "user_prompt": query,
            "session_id": session_id,
            "artifact_file_id": artifact_file_id,
        }

        logger.info(f"[ImageGenerationAgent] Invoking with inputs: {inputs}")
        return self.image_crew.kickoff(inputs)

    async def stream(self, query: str) -> AsyncIterable[Dict[str, Any]]:
        raise NotImplementedError("Streaming is not supported by this agent.")

    def get_image_data(self, session_id: str, image_key: str) -> Imagedata:
        cache = InMemoryCache()
        session_data = cache.get(session_id) or {}
        image = session_data.get(image_key)
        if not image:
            logger.warning(f"[ImageGenerationAgent] Image not found for key: {image_key}")
            return Imagedata(error="Image not found.")
        return image

    def _extract_artifact_file_id(self, query: str) -> Optional[str]:
        match = re.search(r"(?:id|artifact-file-id)\s+([0-9a-f]{32})", query)
        return match.group(1) if match else None
