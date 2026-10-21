"""
Redis state implementation
"""

import pickle
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from typing import Any, cast

from redis.asyncio.client import Redis as AsyncRedis
from redis.client import Redis as SyncRedis

from mr.states.interface import NO_TTL, IState, Ttl


class RedisState(IState):
    """
    State that use hash table to save cached returns
    """

    __async_state: AsyncRedis | None = None
    __sync_state: SyncRedis | None = None
    redis_url: str

    @contextmanager
    def _sync_state(self) -> Iterator[SyncRedis]:
        """
        Get redis sync client
        :return: SyncRedis
        """

        if self.__sync_state is None:
            self.__sync_state = SyncRedis.from_url(url=self.redis_url)
        yield self.__sync_state

    @asynccontextmanager
    async def _async_state(self) -> AsyncIterator[AsyncRedis]:
        """
        Get redis async client
        :return: AsyncRedis
        """
        if self.__async_state is None:
            self.__async_state = AsyncRedis.from_url(url=self.redis_url)
        yield self.__async_state

    def __init__(self, **kwargs: Any) -> None:
        try:
            self.redis_url = kwargs["REDIS_URL"]
        except KeyError as exception:
            raise KeyError("The config value REDIS_URL was not informed") from exception

    @staticmethod
    def _expiry(ttl: Ttl) -> int | None:
        return ttl if isinstance(ttl, int) else None

    def sync_get(self, key: str) -> Any:
        with self._sync_state() as state:
            if value := state.get(key):
                return pickle.loads(cast(bytes, value))
        return None

    def sync_set(self, key: str, value: Any, ttl: Ttl = NO_TTL) -> None:
        with self._sync_state() as state:
            state.set(key, pickle.dumps(value), ex=self._expiry(ttl), nx=True)

    def sync_unset(self, key: str) -> None:
        with self._sync_state() as state:
            state.delete(key)

    async def async_get(self, key: str) -> Any:
        async with self._async_state() as state:
            if value := await state.get(key):
                return pickle.loads(cast(bytes, value))
        return None

    async def async_set(self, key: str, value: Any, ttl: Ttl = NO_TTL) -> None:
        async with self._async_state() as state:
            await state.set(key, pickle.dumps(value), ex=self._expiry(ttl), nx=True)

    async def async_unset(self, key: str) -> None:
        async with self._async_state() as state:
            await state.delete(key)
