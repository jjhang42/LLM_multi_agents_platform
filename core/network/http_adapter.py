# core/network/http_adapter.py
from core.network.network_adapter_base import NetworkAdapterBase
import httpx

class HTTPAdapter(NetworkAdapterBase):
    def __init__(self, broker_url: str):
        self.broker_url = broker_url

    async def send(self, destination: str, payload: dict):
        async with httpx.AsyncClient() as client:
            response = await client.post(destination, json=payload)
            response.raise_for_status()
            return response.json()

    async def receive(self):
        raise NotImplementedError("HTTP mode does not support server push.")

    async def publish(self, topic: str, message: dict):
        # HTTP에서는 publish = send와 동일하게 처리
        return await self.send(f"{self.broker_url}/{topic}", message)

    async def subscribe(self, topic: str, handler):
        raise NotImplementedError("HTTP does not support subscribe natively.")
