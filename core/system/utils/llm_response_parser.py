import json
from datetime import datetime, timezone
from typing import Any, List, Type, TypeVar
from uuid import uuid4
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

def extract_json_list_block(text: str) -> str | None:
    """
    포인터 스캔 방식으로 가장 바깥의 JSON 리스트 블록 추출
    (예: [ {...}, {...} ])
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
    LLM의 raw 응답에서 Task 리스트를 추출하고 필수 필드를 자동 보완합니다.
    - `parameters`, `type`, `action`, `target` 등은 `metadata`로 이동
    - `depends`도 `metadata`에 포함
    - 상태/시간/입력 메시지는 자동 생성
    - 불완전하거나 잘못된 JSON 블록은 무시
    """
    json_block = extract_json_list_block(text)
    if not json_block:
        print("[Parser] JSON 리스트 블록을 찾지 못했습니다.")
        return []

    try:
        parsed_list = json.loads(json_block)
    except json.JSONDecodeError as e:
        print(f"[Parser] JSON decode error: {e}")
        return []

    if not isinstance(parsed_list, list):
        print("[Parser] 파싱된 JSON이 리스트 형식이 아닙니다.")
        return []

    results: List[T] = []
    prev_id: str | None = None
    counter = 1

    for task in parsed_list:
        if not isinstance(task, dict):
            continue

        # ✅ 기본 필드 보완
        task["id"] = task.get("id", f"task_{counter:02d}")
        task["session_id"] = task.get("session_id", uuid4().hex)
        counter += 1

        # ✅ metadata 구성
        metadata = task.get("metadata", {})

        # ⬇️ parameters 안의 action, target 추출 후 metadata로 이동
        parameters = task.get("parameters", {})
        for key in ["action", "target", "type"]:
            if key in parameters and key not in metadata:
                metadata[key] = parameters[key]
        task.pop("parameters", None)

        # ✅ depends 보완
        if "depends" not in metadata or not isinstance(metadata["depends"], list):
            metadata["depends"] = [prev_id] if prev_id else []

        task["metadata"] = metadata

        # ✅ status, message 자동 보완
        task["status"] = task.get("status", {})
        task["status"]["state"] = task["status"].get("state", "submitted")
        task["status"]["timestamp"] = str(datetime.now(timezone.utc).isoformat())

        if (
            "message" not in task["status"]
            or "parts" not in task["status"]["message"]
            or not task["status"]["message"]["parts"]
        ):
            task["status"]["message"] = {
                "role": "user",
                "parts": [{
                    "type": "text",
                    "text": user_input,
                    "metadata": {
                        "timestamp": str(datetime.now(timezone.utc).isoformat())
                    }
                }]
            }

        # ✅ 모델 검증 및 추가
        try:
            parsed = model_class.parse_obj(task)
            results.append(parsed)
            prev_id = task["id"]
        except ValidationError as ve:
            print("[Parser] Validation error:", ve)

    return results
