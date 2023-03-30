import hashlib
import inspect
from typing import TypeVar

import meeseeks

from mr_mime.config import Config
from mr_mime.states.factory import StateFactory
from mr_mime.states.interface import IState
from mr_mime.states.type import StateType

T = TypeVar("T")


@meeseeks.OnlyOne(by_args_hash=True)
class Mime:
    _config: Config = Config(type=StateType.MEMORY)
    _state: IState = None

    @classmethod
    def set_config(cls, config: Config):
        cls._config = config

    def __init__(self, ttl: int):
        self._ttl = ttl

    @classmethod
    def acquire_state(cls) -> IState:
        if cls._state is None:
            cls._state = StateFactory.get_state(config=cls._config)
        return cls._state

    @staticmethod
    def _hash_args(args: tuple, kwargs: dict) -> str:
        """
        Created for each arg + kwargs hash. The kwargs`s order doesn't have influence
        """
        hash_args = [str(arg) for arg in args]
        hash_kwargs = [f"{str(key)}{str(arg)}" for key, arg in kwargs.items()]
        hash_kwargs.sort()
        hash_instance = hashlib.sha1(f"{hash_args}{hash_kwargs}".encode())
        return hash_instance.hexdigest()

    def __call__(self, function: T) -> T:
        is_async = inspect.iscoroutinefunction(function)

        if is_async:
            async def async_mimic(*args, **kwargs):
                args_hash = self._hash_args(args=args, kwargs=kwargs)
                state = self.acquire_state()
                if cached_value := await state.async_get(key=args_hash):
                    return cached_value
                value = await function(*args, **kwargs)
                await state.async_set(key=args_hash, value=value, ttl=self._ttl)
                return value

            mimic = async_mimic
        else:
            def sync_mimic(*args, **kwargs):
                args_hash = self._hash_args(args=args, kwargs=kwargs)
                state = self.acquire_state()
                if cached_value := state.sync_get(key=args_hash):
                    return cached_value
                value = function(*args, **kwargs)
                state.sync_set(key=args_hash, value=value, ttl=self._ttl)
                return value

            mimic = sync_mimic
        mimic.__wrapped__ = function
        return mimic


if __name__ == "__main__":
    import time

    @Mime(ttl=1)
    def teste(a, b, c):
        print("entrou")
        return a + b + c

    a = teste(1,2,3)
    b = teste(1,2,3)
    time.sleep(2)
    c = teste(1, 2, 3)
    d = teste(2, 2, 3)
    print()
