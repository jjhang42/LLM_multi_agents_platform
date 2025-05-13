import json
from datetime import datetime, timezone
from typing import Any, List, Type, TypeVar
from uuid import uuid4
from pydantic import BaseModel, ValidationError
from core.system.utils.clean_json_like_block import clean_json_like_block

T = TypeVar("T", bound=BaseModel)

def extract_json_list_block(text: str) -> str | None:
    """
    포인터 스캔 방식으로 가장 바깥의 JSON 리스트 블록 추출
    """
    start = text.find("[")
    if start == -1:
        return None

    depth = 0
    for i in range(start, len(text)):
        if text[i] == "[":
            depth += 1
        elif text[i] == "]":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None

def llm_response_parser(text: str, model_class: Type[T], user_input: str = "") -> List[T]:
    """
    LLM의 응답 텍스트에서 Task 리스트 추출 및 필수 필드 보완
    - JSON 파싱 전 출력 확인 및 에러 방지
    - dict 또는 list 형태 모두 대응
    """
    print("\U0001f8be [Parser] LLM 원문 출력 ↓↓↓")
    print(text.strip()[:1000] + ("\n... (truncated)" if len(text) > 1000 else ""))
    print("\U0001f50d JSON 블록 추출 시도 중...")

    json_block = clean_json_like_block(text)
    if not json_block:
        print("❌ [Parser] JSON 리스트 블록을 찾지 못했습니다.")
        return []

    try:
        parsed_list = json.loads(json_block)
        if isinstance(parsed_list, dict) and "tasks" in parsed_list:
            parsed_list = parsed_list["tasks"]
    except json.JSONDecodeError as e:
        print(f"❌ [Parser] JSON decode error: {e}")
        print("💡 원본 JSON 블록:\n" + json_block)
        return []

    if not isinstance(parsed_list, list):
        print("❌ [Parser] 파싱된 JSON이 리스트 형식이 아닙니다.")
        return []

    results: List[T] = []
    prev_id: str | None = None
    counter = 1

    for task in parsed_list:
        if not isinstance(task, dict):
            continue

        task["id"] = task.get("id", f"task_{counter:02d}")
        task["session_id"] = task.get("session_id", uuid4().hex)
        counter += 1

        metadata = task.get("metadata", {})
        parameters = task.pop("parameters", {})
        for key in ["action", "target", "type"]:
            if key in parameters and key not in metadata:
                metadata[key] = parameters[key]

        if not metadata.get("action"):
            metadata["action"] = "unknown"

        if not isinstance(metadata.get("depends"), list):
            metadata["depends"] = [prev_id] if prev_id else []

        task["metadata"] = metadata

        status = task.get("status", {})
        if not isinstance(status, dict):
            status = {}

        status["state"] = status.get("state", "submitted")
        status["timestamp"] = status.get("timestamp", str(datetime.now(timezone.utc).isoformat()))

        message = status.get("message", {})
        if not isinstance(message, dict):
            message = {}

        message["role"] = message.get("role", "user")

        parts = message.get("parts", [])
        if not isinstance(parts, list) or not parts:
            message["parts"] = [{
                "type": "text",
                "text": user_input,
                "metadata": {
                    "timestamp": str(datetime.now(timezone.utc).isoformat())
                }
            }]

        status["message"] = message
        task["status"] = status

        try:
            parsed = model_class.parse_obj(task)
            results.append(parsed)
            prev_id = task["id"]
        except ValidationError as ve:
            print(f"❌ [Parser] Validation error for task {task['id']}: {ve}")

    return results
