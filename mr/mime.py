"""
Mr Mime is a function decorator for cache/memoization
"""

import hashlib
import inspect
from typing import TypeVar

import meeseeks

from mr.config import Config
from mr.states.implementations.memory import MemoryState
from mr.states.interface import IState

T = TypeVar("T")


singleton_container = meeseeks.OnlyOne(by_args_hash=True)


@singleton_container
class Mime:
    """
    Decorator to aplay cache/memoization on your functions
    """

    _config: Config = Config(state=MemoryState)
    _state: IState = None

    @classmethod
    def set_config(cls, config: Config):
        """
        Replace the default config

        :param config: Config. IS a instance os Config class
        :return: None
        """
        cls._config = config

    def __init__(self, ttl: int = None):
        self._ttl = ttl

    @classmethod
    def _acquire_state(cls) -> IState:
        if cls._state is None:
            cls._state = cls._config.state()
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
                state = self._acquire_state()
                if cached_value := await state.async_get(key=args_hash):
                    return cached_value
                value = await function(*args, **kwargs)
                await state.async_set(key=args_hash, value=value, ttl=self._ttl)
                return value

            mimic = async_mimic
        else:

            def sync_mimic(*args, **kwargs):
                args_hash = self._hash_args(args=args, kwargs=kwargs)
                state = self._acquire_state()
                if cached_value := state.sync_get(key=args_hash):
                    return cached_value
                value = function(*args, **kwargs)
                state.sync_set(key=args_hash, value=value, ttl=self._ttl)
                return value

            mimic = sync_mimic
        mimic.__wrapped__ = function
        return mimic
