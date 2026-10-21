"""
State interface. You can implement your own State approach
"""

from abc import ABC, abstractmethod
from inspect import _empty
from typing import Any

#: Sentinel used as the default ``ttl`` meaning "this cache entry never expires".
NO_TTL = _empty

#: A time-to-live in seconds, or :data:`NO_TTL` to live forever.
Ttl = int | type[_empty]


class IState(ABC):
    """
    State interface
    """

    @abstractmethod
    def __init__(self, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def sync_get(self, key: str) -> Any:
        """
        Sync get implementation
        :param key: str
        :return:
        """

    @abstractmethod
    def sync_unset(self, key: str) -> None:
        """
        Sync unset implementation
        :param key: str
        :return:
        """

    @abstractmethod
    def sync_set(self, key: str, value: Any, ttl: Ttl) -> None:
        """
        Sync set implementation
        :param key: str
        :param value: Any
        :param ttl: int. Seconds that the cache will have to live. Set NO_TTL to never die
        :return:
        """

    @abstractmethod
    async def async_get(self, key: str) -> Any:
        """
        Async get implementation
        :param key: str
        :return:
        """

    @abstractmethod
    async def async_set(self, key: str, value: Any, ttl: Ttl) -> None:
        """
        Async set implementation
        :param key: str
        :param value: Any
        :param ttl: int. Seconds that the cache will have to live. Set NO_TTL to never die
        :return:
        """

    @abstractmethod
    async def async_unset(self, key: str) -> None:
        """
        Async unset implementation
        :param key: str
        :return:
        """
