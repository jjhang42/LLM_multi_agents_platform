import os
import time
import logging
from dotenv import load_dotenv
from agent_publisher.agent.core import MarkdownPublisherAgent
from agent_publisher.task.manager import AgentTaskManager
from agent_publisher.routes.endpoints import register_routes
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
        name="Publisher Agent",
        description="An A2A-compatible agent that publishes markdown reports to platforms like Notion or blogs.",
        url=f"http://agent_publisher:{port}/",
        version="1.0.0",
        defaultInputModes=["text", "text/plain"],
        defaultOutputModes=["text", "text/markdown"],
        capabilities=AgentCapabilities(streaming=False),
        authentication=AgentAuthentication(
            type="push",
            schemes=["http"],
            push=PushAuthentication(type="none", schemes=[]),
            credentials=None,
        ),
        skills=[
            AgentSkill(
                id="publish_report",
                name="Report Publisher",
                description="Publishes a markdown document as a report to external destinations.",
                tags=["publish", "markdown", "share", "external"],
                examples=[
                    "Publish this summary as a blog post",
                    "Send this analysis to Notion",
                ],
            )
        ],
    )

def main():
    host = "0.0.0.0"
    internal_port = int(os.getenv("AGENT_PUBLISHER_PORT", 8013))

    agent = MarkdownPublisherAgent()
    task_manager = AgentTaskManager(agent)
    agent_card = build_agent_card(internal_port)

    server = A2AServer(
        agent_card=agent_card,
        task_manager=task_manager,
        host=host,
        port=internal_port,
    )

    register_routes(server, agent_card, START_TIME)

    logger.info(f"✅ publisher agent started on http://{host}:{internal_port}/")
    server.start()

if __name__ == "__main__":
    main()
