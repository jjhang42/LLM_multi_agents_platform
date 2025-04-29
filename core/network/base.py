from abc import ABC, abstractmethod
from typing import Any, Callable

class NetworkAdapterBase(ABC):
    @abstractmethod
    async def send(self, destination: str, payload: dict) -> Any:
        """Task나 메시지를 대상(destination)으로 전송하는 메소드"""
        pass

    @abstractmethod
    async def receive(self) -> dict:
        """(옵션) 메시지를 수신하는 메소드"""
        pass

    @abstractmethod
    async def publish(self, topic: str, message: dict):
        """특정 토픽으로 메시지를 퍼블리시하는 메소드 (Pub/Sub 패턴)"""
        pass

    @abstractmethod
    async def subscribe(self, topic: str, handler: Callable):
        """특정 토픽을 구독하고, 메시지가 올 때 핸들러를 실행하는 메소드"""
        pass