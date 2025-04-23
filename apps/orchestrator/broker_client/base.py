from abc import ABC, abstractmethod

class MessageBroker(ABC):
    @abstractmethod
    async def send(self, topic: str, message: dict):
        pass
