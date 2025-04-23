from core.system.config import settings
from .http_transport import HttpTransport
# from .nats_transport import NatsTransport
# from .redis_transport import RedisTransport

class TransportInterface:
    async def send(self, topic: str, payload: dict):
        raise NotImplementedError


_transport_instance: TransportInterface | None = None


def get_transport() -> TransportInterface:
    global _transport_instance
    if _transport_instance is None:
        if settings.BROKER_TYPE == "http":
            _transport_instance = HttpTransport()
        # elif settings.BROKER_TYPE == "nats":
        #     _transport_instance = NatsTransport()
        # elif settings.BROKER_TYPE == "redis":
        #     _transport_instance = RedisTransport()
        else:
            raise ValueError(f"Unsupported BROKER_TYPE: {settings.BROKER_TYPE}")
    return _transport_instance
