from typing import Any
from datetime import datetime
from pydantic import BaseModel
import json


def serialize(obj: Any) -> Any:
    """
    공통 직렬화 함수
    - Pydantic 모델: .model_dump(mode="json")
    - datetime: ISO 포맷
    - dict: 재귀 처리
    - list/tuple: 내부 항목 재귀 처리
    - 그 외: 그대로 반환
    """
    if isinstance(obj, BaseModel):
        return obj.model_dump(mode="json")

    if isinstance(obj, datetime):
        return obj.isoformat()

    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}

    if isinstance(obj, (list, tuple)):
        return [serialize(v) for v in obj]

    return obj


def pretty_json(data: Any) -> str:
    """
    데이터를 보기 좋은 JSON 문자열로 변환합니다.
    - 내부적으로 serialize()를 사용하여 안전하게 처리합니다.
    """
    serialized = serialize(data)
    return json.dumps(serialized, indent=2, ensure_ascii=False)
