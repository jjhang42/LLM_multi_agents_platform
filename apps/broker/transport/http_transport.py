import httpx
from core.system.config import get_broker_url

class HttpTransport:
    def __init__(self):
        self.timeout = httpx.Timeout(30.0)  # 30초 타임아웃 설정

    async def send(self, topic: str, payload: dict) -> httpx.Response:
        endpoint = "task" if "task" in topic else "trace"
        url = get_broker_url(endpoint)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                print(f"[HttpTransport] POST to {url} → {response.status_code}")
                print(f"[HttpTransport] Payload: {payload}")
                response = await client.post(url, json=payload)
                print(f"[HttpTransport] ✅ POST to {url} → {response.status_code}")
                return response
        except httpx.RequestError as e:
            print(f"[HttpTransport] Error sending POST to {url}: {e}")
            raise

# 선택적으로 사용할 수 있는 클로즈 함수 (세션을 명시적으로 닫고 싶을 때)
    async def close(self):
        pass  # AsyncClient는 context manager 내부에서 자동 종료되므로, 여기선 무의미함
