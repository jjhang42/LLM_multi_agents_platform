# core/system/parser/task_input_injector.py

from typing import Dict, Union
from datetime import datetime
from core.system.formats.a2a import TextPart, Message

def inject_input_text_to_tasks(tasks: dict, user_input: str) -> None:
    now = datetime.utcnow()

    for task in tasks.values():
        if isinstance(task, dict):
            task["metadata"] = task.get("metadata", {})
            task["metadata"]["input_text"] = user_input
        else:
            task.status.timestamp = now

            task.status.message = Message(
                role="user",
                parts=[
                    TextPart(
                        type="text",
                        text=user_input,
                        metadata={"timestamp": now.isoformat()}
                    )
                ]
            )