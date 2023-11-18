"""
Mr Mime is a function decorator for cache/memoization
"""
import functools
import inspect
import itertools
from inspect import _empty
from typing import TypeVar, Hashable

import meeseeks

from mr.config import Config
from mr.states.implementations.memory import MemoryState

T = TypeVar("T")

singleton_container = meeseeks.OnlyOne(by_args_hash=True)


@singleton_container
class Mime:
    """
    Decorator to aplay cache/memoization on your functions
    """

    _config: Config = Config(state=MemoryState)

    @classmethod
    def set_config(cls, config: Config):
        """
        Replace the default config

        :param config: Config. IS a instance os Config class
        :return: None
        """
        cls._config = config

    def __init__(self, ttl: int = _empty):
        self._ttl = ttl

    @staticmethod
    def _hash_args(func_hash: int, args: tuple, kwargs: dict) -> int:
        """
        Created for each arg + kwargs hash. The kwargs`s order doesn't have influence
        """
        hash_instance = tuple(
            item if isinstance(item, Hashable) else str(item)
            for item in itertools.chain(
                [func_hash], args, [i[1] for i in sorted(kwargs.items())]
            )
        )
        return hash(hash_instance)

    def __call__(self, callable_obj: T) -> T:
        _is_class = inspect.isclass(callable_obj)
        if inspect.isclass(callable_obj):
            raise TypeError(
                "Mr. Mime don`t support class memoization for this use meeseeks-singleton package\n"
                "link: https://pypi.org/project/meeseeks-singleton/"
            )
        _func_hash = hash(callable_obj)
        if inspect.iscoroutinefunction(callable_obj):

            @functools.wraps(callable_obj)
            async def async_mimic(*args, **kwargs):
                args_hash = self._hash_args(
                    func_hash=_func_hash, args=args, kwargs=kwargs
                )
                async with self._config.async_acquire_state() as state:
                    if cached_value := await state.async_get(key=args_hash):
                        return cached_value
                    value = await callable_obj(*args, **kwargs)
                    await state.async_set(key=args_hash, value=value, ttl=self._ttl)
                    return value

            return async_mimic

        @functools.wraps(callable_obj)
        def sync_mimic(*args, **kwargs):
            args_hash = self._hash_args(func_hash=_func_hash, args=args, kwargs=kwargs)
            with self._config.sync_acquire_state() as state:
                if cached_value := state.sync_get(key=args_hash):
                    return cached_value
                value = callable_obj(*args, **kwargs)
                state.sync_set(key=args_hash, value=value, ttl=self._ttl)
                return value

        return sync_mimic
