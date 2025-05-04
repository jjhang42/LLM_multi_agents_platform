# core/system/utils/serialize.py
from typing import Any
from datetime import datetime
from pydantic import BaseModel


def serialize(obj: Any) -> Any:
    """
    공통 직렬화 함수
    - Pydantic 모델: model_dump(mode="json")
    - datetime: ISO 포맷
    - dict: 재귀 처리
    - 리스트/튜플: 내부 항목 순환
    - 기본 객체: 그대로 반환
    """
    if isinstance(obj, BaseModel):
        return obj.model_dump(mode="json")

    elif isinstance(obj, datetime):
        return obj.isoformat()

    elif isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}

    elif isinstance(obj, (list, tuple)):
        return [serialize(v) for v in obj]

    else:
        return obj
