from inspect import _empty
from random import randint
from uuid import uuid4

import pytest
from freezegun import freeze_time

from mr.states import MemoryState


def test_sync_set():
    state = MemoryState()
    with freeze_time("2023-01-14 12:00:01"):
        state.sync_set(1, 10, 1)
    assert state._state == {1: {"created_at": 1673697601.0, "ttl": 1, "value": 10}}


@pytest.mark.asyncio
async def test_async_set():
    state = MemoryState()
    with freeze_time("2023-01-14 12:00:01"):
        await state.async_set(1, 10)
    assert state._state == {1: {"created_at": 1673697601.0, "ttl": _empty, "value": 10}}


@pytest.fixture()
def state_with_data():
    state = MemoryState()
    with freeze_time("2023-01-14 12:00:00"):
        data = [1, randint(1, 10), randint(1, 10)]
        state.sync_set(*data)
    return state, data


def test_sync_get_without_data(state_with_data):
    state, data = state_with_data
    value = state.sync_get(key=1)
    assert value is None


def test_sync_get_expired_ttl():
    state = MemoryState()
    with freeze_time("2023-01-14 12:00:00"):
        data = [1, randint(1, 10), 1]
        state.sync_set(*data)
    with freeze_time("2023-01-14 12:00:01"):
        value = state.sync_get(key=1)
    assert value == data[1]


def test_sync_get(state_with_data):
    state, data = state_with_data
    with freeze_time("2023-01-14 12:00:00"):
        value = state.sync_get(data[0])
    assert value == data[1]


def test_sync_get_without_ttl_set(state_with_data):
    state = MemoryState()
    data = [1, randint(1, 10)]
    state.sync_set(*data)
    value = state.sync_get(data[0])
    assert value == data[1]


@pytest.mark.asyncio
async def test_async_get_without_data(state_with_data):
    state, data = state_with_data
    value = await state.async_get(1)
    assert value is None


@pytest.mark.asyncio
async def test_async_get_expired_ttl(state_with_data):
    state, data = state_with_data
    with freeze_time("2023-01-14 13:00:00"):
        value = await state.async_get(1)
    assert value is None


@pytest.mark.asyncio
async def test_async_get(state_with_data):
    state, data = state_with_data
    with freeze_time("2023-01-14 12:00:00"):
        value = await state.async_get(data[0])
    assert value == data[1]


@pytest.mark.asyncio
async def test_async_get_without_ttl_set(state_with_data):
    state = MemoryState()
    data = [1, randint(1, 10)]
    await state.async_set(*data)
    value = await state.async_get(data[0])
    assert value == data[1]
