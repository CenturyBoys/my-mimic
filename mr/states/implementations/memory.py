"""
Memory state implementation
"""

from datetime import datetime

from mr.states.interface import IState


class MemoryState(IState):
    """
    State that use hash table to save cached returns
    """

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self._state = {}

    def sync_get(self, key: str):
        now_timestamp = datetime.utcnow().timestamp()
        if register := self._state.get(key):
            register_timestamp = register.get("created_at")
            ttl = register.get("ttl")
            if ttl is None or ((register_timestamp + ttl) >= now_timestamp):
                return register.get("value")
        return None

    def sync_set(self, key: str, value: any, ttl: int = None):
        self._state.update(
            {
                key: {
                    "created_at": datetime.utcnow().timestamp(),
                    "ttl": ttl,
                    "value": value,
                }
            }
        )

    async def async_get(self, key: str):
        return self.sync_get(key)

    async def async_set(self, key: str, value: any, ttl: int = None):
        return self.sync_set(key=key, value=value, ttl=ttl)
