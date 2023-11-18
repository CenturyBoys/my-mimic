"""
Memory state implementation
"""
import pickle
from contextlib import contextmanager, asynccontextmanager
from inspect import _empty

from redis.asyncio.client import Redis as AsyncRedis
from redis.client import Redis as SyncRedis


from mr.states.interface import IState


class RedisState(IState):
    """
    State that use hash table to save cached returns
    """

    __async_state: AsyncRedis = None
    __sync_state: SyncRedis = None

    @contextmanager
    def _sync_state(self) -> SyncRedis:
        """
        Get redis sync client
        :return: SyncRedis
        """

        if self.__sync_state is None:
            self.__sync_state = SyncRedis.from_url(url=self.redis_url)
        yield self.__sync_state

    @asynccontextmanager
    async def _async_state(self) -> AsyncRedis:
        """
        Get redis async client
        :return: SyncRedis
        """
        if self.__async_state is None:
            self.__async_state = AsyncRedis.from_url(url=self.redis_url)
        yield self.__async_state

    def __init__(self, **kwargs):
        try:
            self.redis_url = kwargs["REDIS_URL"]
        except KeyError as exception:
            raise KeyError("The config value REDIS_URL was not informed") from exception

    def sync_get(self, key: int):
        with self._sync_state() as state:
            if value := state.get(key):
                return pickle.loads(value)
        return None

    def sync_set(self, key: int, value: any, ttl: int = _empty):
        with self._sync_state() as state:
            state.set(key, pickle.dumps(value), ex=ttl, nx=True)

    async def async_get(self, key: int):
        async with self._async_state() as state:
            if value := await state.get(key):
                return pickle.loads(value)
        return None

    async def async_set(self, key: int, value: any, ttl: int = _empty):
        async with self._async_state() as state:
            await state.set(key, pickle.dumps(value), ex=ttl, nx=True)
