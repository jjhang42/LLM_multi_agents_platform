# apps/orchestrator/broker_client/http_broker.py

import httpx
from core.system.config import get_broker_url
from .base import MessageBroker


class HttpBroker(MessageBroker):
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)

    async def send(self, topic: str, message: dict):
        endpoint = "task" if "task" in topic else "trace"
        url = get_broker_url(endpoint)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=message)
                print(f"[HttpBroker] POST to {url} → {response.status_code}")

                if response.status_code >= 400:
                    print(f"[HttpBroker] Error response: {response.text}")
                    raise Exception(f"HTTP {response.status_code}: {response.text}")

                return response

        except httpx.RequestError as e:
            print(f"[HttpBroker] 🔌 Connection error to {url}: {str(e)}")
            raise
