"""
Memory state implementation
"""

from datetime import datetime, timezone
from typing import Any

from mr.states.interface import NO_TTL, IState, Ttl


class MemoryState(IState):
    """
    State that use hash table to save cached returns
    """

    _state: dict[str, Any]
    _kwargs: dict[str, Any]

    __slots__ = ("_state", "_kwargs")

    def __init__(self, **kwargs: Any) -> None:
        self._kwargs = kwargs
        self._state = {}

    def sync_get(self, key: str) -> Any:
        now_timestamp = datetime.now(timezone.utc).timestamp()
        if register := self._state.get(key):
            _ttl = register.get("ttl")
            if _ttl == NO_TTL or ((register.get("created_at") + _ttl) >= now_timestamp):
                return register.get("value")
        return None

    def sync_set(self, key: str, value: Any, ttl: Ttl = NO_TTL) -> None:
        record = {
            "created_at": datetime.now(timezone.utc).timestamp(),
            "ttl": ttl,
            "value": value,
        }
        self._state.update({key: record})

    def sync_unset(self, key: str) -> None:
        if key in self._state:
            del self._state[key]
        return None

    async def async_get(self, key: str) -> Any:
        return self.sync_get(key)

    async def async_set(self, key: str, value: Any, ttl: Ttl = NO_TTL) -> None:
        self.sync_set(key=key, value=value, ttl=ttl)

    async def async_unset(self, key: str) -> None:
        self.sync_unset(key)
