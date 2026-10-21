"""
Mr Mime is a function decorator for cache/memoization
"""

import functools
import hashlib
import inspect
import itertools
from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import asynccontextmanager, contextmanager
from typing import Any, TypeVar, cast

import meeseeks

from mr.config import Config
from mr.states.implementations.memory import MemoryState
from mr.states.interface import NO_TTL, IState, Ttl

T = TypeVar("T", bound=Callable[..., Any])
_C = TypeVar("_C")

singleton_container = cast(Callable[[_C], _C], meeseeks.OnlyOne(by_args_hash=True))


@singleton_container
class Mime:
    """
    Decorator to aplay cache/memoization on your functions
    """

    _config: Config = Config(state=MemoryState)

    @classmethod
    def set_config(cls, config: Config) -> None:
        """
        Replace the default config

        :param config: Config. IS an instance os Config class
        :return: None
        """
        cls._config = config

    def __init__(self, ttl: Ttl = NO_TTL) -> None:
        self._ttl = ttl

    @staticmethod
    def _hash_args(
        func_name: str, args: tuple[Any, ...], kwargs: dict[str, Any]
    ) -> str:
        """
        Created for each arg + kwargs hash. The kwargs`s order doesn't have influence
        """
        hash_instance = "".join(
            str(item)
            for item in itertools.chain(
                [func_name], args, [i[1] for i in sorted(kwargs.items())]
            )
        )
        return hashlib.sha256(hash_instance.encode()).hexdigest()

    @asynccontextmanager
    async def async_acquire_state(self) -> AsyncIterator[IState]:
        """
        Acquire the current state implementation asynchronous
        """
        async with self._config.async_acquire_state() as state:
            yield state

    @contextmanager
    def sync_acquire_state(self) -> Iterator[IState]:
        """
        Acquire the current state implementation synchronous
        """
        with self._config.sync_acquire_state() as state:
            yield state

    def __call__(self, callable_obj: T) -> T:
        if inspect.isclass(callable_obj):
            raise TypeError(
                "Mr. Mime don`t support class memoization for this use meeseeks-singleton package\n"
                "link: https://pypi.org/project/meeseeks-singleton/"
            )
        func_name = getattr(callable_obj, "__name__", "")
        if inspect.iscoroutinefunction(callable_obj):

            @functools.wraps(callable_obj)
            async def async_mimic(*args: Any, **kwargs: Any) -> Any:
                args_hash = self._hash_args(
                    func_name=func_name, args=args, kwargs=kwargs
                )
                async with self._config.async_acquire_state() as state:
                    if cached_value := await state.async_get(key=args_hash):
                        return cached_value
                    value = await callable_obj(*args, **kwargs)
                    await state.async_set(key=args_hash, value=value, ttl=self._ttl)
                    return value

            async def async_invalidate(*args: Any, **kwargs: Any) -> None:
                """Drop the cached entry for ``callable_obj(*args, **kwargs)``."""
                args_hash = self._hash_args(
                    func_name=func_name, args=args, kwargs=kwargs
                )
                async with self._config.async_acquire_state() as state:
                    await state.async_unset(key=args_hash)

            async_mimic.invalidate = async_invalidate  # type: ignore[attr-defined]
            return cast(T, async_mimic)

        @functools.wraps(callable_obj)
        def sync_mimic(*args: Any, **kwargs: Any) -> Any:
            args_hash = self._hash_args(func_name=func_name, args=args, kwargs=kwargs)
            with self._config.sync_acquire_state() as state:
                if cached_value := state.sync_get(key=args_hash):
                    return cached_value
                value = callable_obj(*args, **kwargs)
                state.sync_set(key=args_hash, value=value, ttl=self._ttl)
                return value

        def invalidate(*args: Any, **kwargs: Any) -> None:
            """Drop the cached entry for ``callable_obj(*args, **kwargs)``."""
            args_hash = self._hash_args(func_name=func_name, args=args, kwargs=kwargs)
            with self._config.sync_acquire_state() as state:
                state.sync_unset(key=args_hash)

        sync_mimic.invalidate = invalidate  # type: ignore[attr-defined]
        return cast(T, sync_mimic)
