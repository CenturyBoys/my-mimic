from datetime import datetime, timedelta
from typing import Type

import pytest
from freezegun import freeze_time

import mr
from mr import Mime, Config
from mr.mime import singleton_container
from mr.states.implementations.memory import MemoryState
from tests.config.test_config import StubState


def test_mime_singleton():
    a1 = Mime(1)
    a2 = Mime(2)
    assert id(a1) != id(a2)


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


def teste_class_error():
    with pytest.raises(TypeError) as exception:

        @mr.Mime()
        class A:
            pass

    assert exception.value.args == (
        "Mr. Mime don`t support class memoization for this use meeseeks-singleton package\n"
        "link: https://pypi.org/project/meeseeks-singleton/",
    )


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

    datetime_now = datetime.utcnow()
    with freeze_time(datetime_now):
        return_a1 = cached_callback(0)
    datetime_now += timedelta(seconds=2)
    with freeze_time(datetime_now):
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

    datetime_now = datetime.utcnow()
    with freeze_time(datetime_now):
        return_a1 = await cached_callback(0)
    datetime_now += timedelta(seconds=2)
    with freeze_time(datetime_now):
        return_a2 = await cached_callback(0)
    assert return_a1 != return_a2
