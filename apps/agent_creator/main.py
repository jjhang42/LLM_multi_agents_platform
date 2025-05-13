import os
import time
import logging
from dotenv import load_dotenv
from agent_creator.agent.core import ImageGenerationAgent
from agent_creator.task.manager import AgentTaskManager
from agent_creator.routes.endpoints import register_routes
from core.server_components.a2a_server import A2AServer
from core.system.formats.agent_card import AgentCard, AgentSkill, AgentCapabilities
from core.system.formats.a2a import AgentAuthentication, PushAuthentication

# 1. 환경 변수 로드
load_dotenv()

# 2. 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 3. 시작 시간 기록
START_TIME = time.time()

def build_agent_card(port: int) -> AgentCard:
    return AgentCard(
        name="Image Generator Agent",
        description="An A2A-compatible agent that creates images from prompts using CrewAI and Gemini.",
        url=f"http://agent_creator:{port}/",
        version="1.0.0",
        defaultInputModes=["text", "text/plain"],
        defaultOutputModes=["image/png"],
        capabilities=AgentCapabilities(streaming=False),
        authentication=AgentAuthentication(
            type="push",
            schemes=["http"],
            push=PushAuthentication(type="none", schemes=[]),
            credentials=None,
        ),
        skills=[
            AgentSkill(
                id="image_generator",
                name="Image Generator",
                description="Generate high-quality images based on natural language prompts.",
                tags=["generate image", "edit image"],
                examples=["Generate a photorealistic image of raspberry lemonade"],
            )
        ],
    )

def main():
    host = "0.0.0.0"
    internal_port = int(os.getenv("AGENT_CREATOR_PORT", 8000))

    agent = ImageGenerationAgent()
    task_manager = AgentTaskManager(agent)
    agent_card = build_agent_card(internal_port)

    server = A2AServer(
        agent_card=agent_card,
        task_manager=task_manager,
        host=host,
        port=internal_port,
    )

    register_routes(server, agent_card, START_TIME)

    logger.info(f"✅ image_generator agent started on http://{host}:{internal_port}/")
    server.start()

if __name__ == "__main__":
    main()
