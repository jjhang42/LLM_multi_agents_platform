from core.system.config import settings
from .http_broker import HttpBroker
# from .nats_broker import NatsBroker  # To be implemented
# from .redis_broker import RedisBroker  # To be implemented
from .base import MessageBroker

def get_broker() -> MessageBroker:
    if settings.BROKER_TYPE == "http":
        return HttpBroker()
    # elif settings.BROKER_TYPE == "nats":
    #     return NatsBroker()
    # elif settings.BROKER_TYPE == "redis":
    #     return RedisBroker()
    else:
        raise ValueError(f"Unsupported BROKER_TYPE: {settings.BROKER_TYPE}")
