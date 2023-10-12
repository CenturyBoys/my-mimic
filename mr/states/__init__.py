"""
Import of  default state and extras
"""
from mr.states.implementations.memory import MemoryState

__all__ = ["MemoryState"]

# Redis edition extra
try:
    import redis.asyncio as redis
    from .implementations.redis import RedisState

    __all__ += "RedisState"
except ImportError as error:  # pragma: no cover
    pass

# Temp edition extra
try:
    from aiofile import async_open
    from .implementations.temp import TempFileState

    __all__ += "TempFileState"
except ImportError as error:  # pragma: no cover
    pass
