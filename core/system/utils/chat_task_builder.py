from datetime import datetime
from core.system.formats.a2a import Task, TaskStatus
from core.system.formats.a2a import TaskState


def make_chat_response_task(response_text: str) -> Task:
    """
    단순 대화 응답용 Task 객체를 생성합니다.
    A2A 프로토콜 구조를 고수하며 status 필드를 반드시 포함합니다.
    """
    return Task(
        id="chat_response",
        session_id="chat",
        status=TaskStatus(
            state=TaskState.COMPLETED,
            message={
                "role": "assistant",
                "parts": [{"type": "text", "text": response_text}]
            },
            timestamp=datetime.utcnow()
        ),
        metadata={"type": "chat"}
    )
