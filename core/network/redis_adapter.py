# core/network/redis_adapter.py
from core.network.network_adapter_base import NetworkAdapterBase
import aioredis
import json

class RedisAdapter(NetworkAdapterBase):
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)

    async def send(self, destination: str, payload: dict):
        # Redis에서는 send = publish
        await self.publish(destination, payload)

    async def publish(self, topic: str, message: dict):
        await self.redis.publish(topic, json.dumps(message))

    async def subscribe(self, topic: str, handler):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(topic)

        async for message in pubsub.listen():
            if message['type'] == 'message':
                payload = json.loads(message['data'])
                await handler(payload)

    async def receive(self):
        # receive는 subscribe를 통해 이루어짐
        raise NotImplementedError("Use subscribe() instead.")
