"""
Memory state implementation
"""
import pickle
from contextlib import contextmanager, asynccontextmanager

from redis.asyncio.client import Redis as AsyncRedis
from redis.client import Redis as SyncRedis


from mr.states.interface import IState


class RedisState(IState):
    """
    State that use hash table to save cached returns
    """

    _async_state: AsyncRedis = None
    _sync_state: SyncRedis = None

    @contextmanager
    def sync_state(self) -> SyncRedis:
        """
        Get redis sync client
        :return: SyncRedis
        """

        if self._sync_state is None:
            self._sync_state = SyncRedis.from_url(url=self.redis_url)
        yield self._sync_state

    @asynccontextmanager
    async def async_state(self) -> AsyncRedis:
        """
        Get redis async client
        :return: SyncRedis
        """
        if self._async_state is None:
            self._async_state = AsyncRedis.from_url(url=self.redis_url)
        yield self._async_state

    def __init__(self, **kwargs):
        try:
            self.redis_url = kwargs["REDIS_URL"]
        except KeyError as exception:
            raise KeyError("The config value REDIS_URL was not informed") from exception

    def sync_get(self, key: str):
        with self.sync_state() as state:
            if value := state.get(key):
                return pickle.loads(value)
        return None

    def sync_set(self, key: str, value: any, ttl: int = None):
        with self.sync_state() as state:
            state.set(key, pickle.dumps(value), ex=ttl, nx=True)

    async def async_get(self, key: str):
        async with self.async_state() as state:
            if value := await state.get(key):
                return pickle.loads(value)
        return None

    async def async_set(self, key: str, value: any, ttl: int = None):
        async with self.async_state() as state:
            await state.set(key, pickle.dumps(value), ex=ttl, nx=True)
