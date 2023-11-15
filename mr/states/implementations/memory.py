"""
Memory state implementation
"""
from datetime import datetime
from inspect import _empty

from mr.states.interface import IState


class MemoryState(IState):
    """
    State that use hash table to save cached returns
    """

    _state: dict[int, any]
    _kwargs: dict[str, any]

    __slots__ = ("_state", "_kwargs")

    def __init__(self, **kwargs):
        self._kwargs = kwargs
        self._state = {}

    def sync_get(self, key: int):
        now_timestamp = datetime.utcnow().timestamp()
        if register := self._state.get(key):
            _ttl = register.get("ttl")
            if _ttl == _empty or ((register.get("created_at") + _ttl) >= now_timestamp):
                return register.get("value")
        return None

    def sync_set(self, key: int, value: any, ttl: int = _empty):
        value = {
            "created_at": datetime.utcnow().timestamp(),
            "ttl": ttl,
            "value": value,
        }
        self._state.update({key: value})

    async def async_get(self, key: int):
        return self.sync_get(key)

    async def async_set(self, key: int, value: any, ttl: int = _empty):
        return self.sync_set(key=key, value=value, ttl=ttl)
