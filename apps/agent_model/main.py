# apps/agent_model/main.py

import os
import time
import logging
from dotenv import load_dotenv
from fastapi import APIRouter
from agent import ImageGenerationAgent
from task_manager import AgentTaskManager
from common.server import A2AServer
from common.types import AgentCard, AgentSkill, AgentCapabilities

# .env 로드
load_dotenv()

# 시작 시간 기록 (uptime용)
START_TIME = time.time()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    host = "0.0.0.0"
    internal_port = int(os.getenv("PORT", 8000))
    external_url = f"http://agent_model:{internal_port}/"

    skill = AgentSkill(
        id="image_generator",
        name="Image Generator",
        description="Generate high-quality images based on natural language prompts.",
        tags=["generate image", "edit image"],
        examples=["Generate a photorealistic image of raspberry lemonade"],
    )

    card = AgentCard(
        name="Image Generator Agent",
        description="An A2A-compatible agent that creates images from prompts using CrewAI and Gemini.",
        url=external_url,
        version="1.0.0",
        defaultInputModes=["text", "text/plain"],
        defaultOutputModes=["image/png"],
        capabilities=AgentCapabilities(streaming=False),
        skills=[skill],
    )

    server = A2AServer(
        agent_card=card,
        task_manager=AgentTaskManager(ImageGenerationAgent()),
        host=host,
        port=internal_port,
    )

    router = APIRouter()

    @router.get("/health")
    def health_check():
        return {
            "status": "ok",
            "service": "image_generator",
            "version": "1.0.0",
            "uptime": f"{time.time() - START_TIME:.2f}s"
        }

    server.app.include_router(router)

    logger.info(f"image_generator agent started on {external_url}")
    server.start()


if __name__ == "__main__":
    main()
