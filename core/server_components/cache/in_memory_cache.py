# core/server_components/cache/in_memory_cache.py
class InMemoryCache:
    """
    Very simple in-memory cache to simulate session-based storage.
    Used to store generated image artifacts by session_id.
    """

    def __init__(self):
        self.cache = {}

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value
