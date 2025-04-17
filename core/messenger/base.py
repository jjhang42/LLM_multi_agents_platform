from abc import ABC, abstractmethod

class MessageBroker(ABC):
    @abstractmethod
    async def publish(self, topic: str, message: dict): ...
    
    @abstractmethod
    async def subscribe(self, topic: str, handler): ...
