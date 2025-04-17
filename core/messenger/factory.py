from core.system.config import settings
from core.messenger.base import MessageBroker

from core.messenger.nats_broker import NatsBroker
from core.messenger.redis_broker import RedisBroker

BROKER_REGISTRY = {
    "nats": NatsBroker,
    "redis": RedisBroker
}

def get_broker() -> MessageBroker:
    broker_type = settings.BROKER_TYPE.lower()
    broker_cls = BROKER_REGISTRY.get(broker_type)

    if not broker_cls:
        raise ValueError(
            f"Unsupported broker type: '{broker_type}'. "
            f"Available types: {', '.join(BROKER_REGISTRY.keys())}"
        )

    return broker_cls()
