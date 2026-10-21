"""
Import of default state and extras
"""

from mr.states.implementations.memory import MemoryState

__all__ = ["MemoryState"]

# Redis edition extra
try:
    from .implementations.redis import RedisState

    __all__ += ["RedisState"]
except ImportError:  # pragma: no cover
    pass

# Temp edition extra
try:
    from .implementations.temp import TempFileState

    __all__ += ["TempFileState"]
except ImportError:  # pragma: no cover
    pass
