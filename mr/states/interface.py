"""
State interface. You can implement your own State approach
"""

from abc import ABC, abstractmethod


class IState(ABC):
    """
    State interface
    """

    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def sync_get(self, key: str):
        """
        Sync get implementation
        :param key: str
        :return:
        """

    @abstractmethod
    def sync_set(self, key: str, value: any, ttl: int):
        """
        Sync set implementation
        :param key: str
        :param value: Any
        :param ttl: int. Seconds that the cache will have to live. Set None to never die
        :return:
        """

    @abstractmethod
    async def async_get(self, key: str):
        """
        Async get implementation
        :param key: str
        :return:
        """

    @abstractmethod
    async def async_set(self, key: str, value: any, ttl: int):
        """
        Async set implementation
        :param key: str
        :param value: Any
        :param ttl: int. Seconds that the cache will have to live. Set None to never die
        :return:
        """
