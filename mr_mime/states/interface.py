from abc import ABC, abstractmethod


class IState(ABC):

    @abstractmethod
    def sync_get(self, key: str):
        pass

    @abstractmethod
    def sync_set(self, key: str, value: any, ttl: int = None):
        pass

    @abstractmethod
    async def async_get(self, key: str):
        pass

    @abstractmethod
    async def async_set(self, key: str, value: any, ttl: int = None):
        pass
