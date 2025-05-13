# core/system/memory/memory_store.py

from typing import List, Dict
from collections import defaultdict
import threading


class InMemoryMemoryStore:
    def __init__(self):
        self._store = defaultdict(list)  # session_id → List[Dict]
        self._lock = threading.Lock()

    def append(self, session_id: str, message: Dict[str, str]):
        """
        message 형식 예시: { "role": "user", "text": "오늘 날씨 알려줘" }
        """
        with self._lock:
            self._store[session_id].append(message)

    def get(self, session_id: str) -> List[Dict[str, str]]:
        with self._lock:
            return list(self._store.get(session_id, []))

    def clear(self, session_id: str):
        with self._lock:
            self._store.pop(session_id, None)
