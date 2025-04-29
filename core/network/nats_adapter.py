# core/network/nats_adapter.py
from core.network.network_adapter_base import NetworkAdapterBase
import nats
import json

class NATSAdapter(NetworkAdapterBase):
    def __init__(self, nats_url: str):
        self.nats_url = nats_url
        self.nc = None

    async def connect(self):
        if not self.nc:
            self.nc = await nats.connect(self.nats_url)

    async def send(self, destination: str, payload: dict):
        await self.connect()
        await self.nc.publish(destination, json.dumps(payload).encode())

    async def publish(self, topic: str, message: dict):
        await self.send(topic, message)

    async def subscribe(self, topic: str, handler):
        await self.connect()

        async def message_handler(msg):
            data = json.loads(msg.data.decode())
            await handler(data)

        await self.nc.subscribe(topic, cb=message_handler)

    async def receive(self):
        # receive는 subscribe를 통해 이루어짐
        raise NotImplementedError("Use subscribe() instead.")
