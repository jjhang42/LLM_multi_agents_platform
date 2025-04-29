# core/network/network_router.py
import os
from core.network.http_adapter import HTTPAdapter
from core.network.redis_adapter import RedisAdapter
from core.network.nats_adapter import NATSAdapter

def get_network_adapter():
    adapter_type = os.getenv("NETWORK_ADAPTER", "http").lower()

    if adapter_type == "http":
        broker_url = os.getenv("BROKER_HTTP_URL")
        return HTTPAdapter(broker_url)
    elif adapter_type == "redis":
        redis_url = os.getenv("REDIS_URL")
        return RedisAdapter(redis_url)
    elif adapter_type == "nats":
        nats_url = os.getenv("NATS_URL")
        return NATSAdapter(nats_url)
    else:
        raise ValueError(f"Unsupported network adapter: {adapter_type}")
