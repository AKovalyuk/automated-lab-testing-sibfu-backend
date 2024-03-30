from redis import Redis

from .config import settings


_client = None


def get_redis_client():
    """Lazy loading redis client"""
    global _client
    if _client is None:
        _client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
    return _client
