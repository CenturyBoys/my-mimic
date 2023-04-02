from datetime import datetime
from typing import Type
import time

import pytest

from mr import Mime, Config
from mr.mime import singleton_container
from mr.states.implementations.memory import MemoryState
from tests.config.test_config import StubState


@pytest.fixture()
def mime_default() -> Type[Mime]:
    singleton_container.clean_references()
    Mime.set_config(config=Config(state=MemoryState))
    return Mime


def test_set_config(mime_default):
    assert issubclass(Mime._config.state, MemoryState)
    new_config = Config(state=StubState)
    mime_default.set_config(config=new_config)
    assert issubclass(Mime._config.state, StubState)


def test_acquire_state(mime_default):
    assert mime_default._state is None
    state = mime_default._acquire_state()
    assert isinstance(mime_default._state, MemoryState)
    assert isinstance(state, MemoryState)


def test_sync_mimic_get_cached_return(mime_default):
    @mime_default(ttl=1)
    def cached_callback(param_a: int):
        return datetime.utcnow().timestamp()

    return_a1 = cached_callback(0)
    return_a2 = cached_callback(0)
    assert return_a1 == return_a2


def test_sync_mimic_get_renew_return(mime_default):
    @mime_default(ttl=1)
    def cached_callback(param_a: int):
        return datetime.utcnow().timestamp()

    return_a1 = cached_callback(0)
    time.sleep(2)
    return_a2 = cached_callback(0)
    assert return_a1 != return_a2


@pytest.mark.asyncio
async def test_async_mimic_get_cached_return(mime_default):
    @mime_default(ttl=1)
    async def cached_callback(param_a: int):
        return datetime.utcnow().timestamp()

    return_a1 = await cached_callback(0)
    return_a2 = await cached_callback(0)
    assert return_a1 == return_a2


@pytest.mark.asyncio
async def test_async_mimic_get_renew_return(mime_default):
    @mime_default(ttl=1)
    async def cached_callback(param_a: int):
        return datetime.utcnow().timestamp()

    return_a1 = await cached_callback(0)
    time.sleep(2)
    return_a2 = await cached_callback(0)
    assert return_a1 != return_a2
