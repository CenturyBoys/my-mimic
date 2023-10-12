import builtins
import os
import tempfile
from pathlib import Path
from random import randint
from tempfile import TemporaryDirectory
from unittest.mock import patch, MagicMock, call
from uuid import uuid4

import pytest
from freezegun import freeze_time

from mr.states import TempFileState


def test_wrong_config():
    with pytest.raises(TypeError) as exception:
        TempFileState(BASE_PATH=10)
    assert exception.value.args[0] == "The config value BASE_PATH is not a valid Path"


def test_default():
    state = TempFileState()
    assert isinstance(state._temp_folder, TemporaryDirectory)
    assert str(state._path) == str(Path(state._temp_folder.name))


def test_static_without_base_path():
    state = TempFileState(STATIC=True)
    assert str(state._path) == str((Path(tempfile.gettempdir())))


def test_static_with_base_path():
    state = TempFileState(STATIC=False, BASE_PATH=os.getcwd())
    assert isinstance(state._temp_folder, TemporaryDirectory)
    assert str(state._path) == str(Path(state._temp_folder.name))
    assert str(Path(state._temp_folder.name)).endswith(state._temp_folder.name)


def test_sync_set():
    state = TempFileState()
    with freeze_time("2023-01-14 12:00:01"):
        mock_object = MagicMock()
        with patch.object(builtins, "open", return_value=mock_object):
            state.sync_set("t1", 10, 1)
    write_bytes_call = call.write(
        b"\x80\x04\x953\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\ncreated_at\x94GA\xd8\xf0\xa6P@\x00\x00\x8c\x03ttl\x94K\x01\x8c\x05value\x94C\x05\x80\x04K\n.\x94u.",
    )
    assert write_bytes_call in mock_object.__enter__().method_calls


@pytest.mark.asyncio
async def test_async_set():
    state = TempFileState()
    with freeze_time("2023-01-14 12:00:01"):
        with patch("aiofile.async_open") as mock_object:
            await state.async_set("t1", 10, 1)
    write_bytes_call = call.write(
        b"\x80\x04\x953\x00\x00\x00\x00\x00\x00\x00}\x94(\x8c\ncreated_at\x94GA\xd8\xf0\xa6P@\x00\x00\x8c\x03ttl\x94K\x01\x8c\x05value\x94C\x05\x80\x04K\n.\x94u.",
    )
    async with mock_object() as a:
        assert write_bytes_call in a.method_calls


@pytest.fixture()
def state_with_data():
    state = TempFileState()
    with freeze_time("2023-01-14 12:00:00"):
        data = [str(uuid4()), randint(1, 10), randint(1, 10)]
        state.sync_set(*data)
    return state, data


def test_sync_get_without_data(state_with_data):
    state, data = state_with_data
    value = state.sync_get("t1")
    assert value is None


def test_sync_get_expired_ttl(state_with_data):
    state, data = state_with_data
    with freeze_time("2023-01-14 13:00:00"):
        value = state.sync_get("t1")
    assert value is None


def test_sync_get(state_with_data):
    state, data = state_with_data
    with freeze_time("2023-01-14 12:00:00"):
        value = state.sync_get(data[0])
    assert value == data[1]


def test_sync_get_without_ttl_set(state_with_data):
    state = TempFileState()
    data = [str(uuid4()), randint(1, 10), None]
    state.sync_set(*data)
    value = state.sync_get(data[0])
    assert value == data[1]


@pytest.mark.asyncio
async def test_async_get_without_data(state_with_data):
    state, data = state_with_data
    value = await state.async_get("t1")
    assert value is None


@pytest.mark.asyncio
async def test_async_get_expired_ttl(state_with_data):
    state, data = state_with_data
    with freeze_time("2023-01-14 13:00:00"):
        value = await state.async_get("t1")
    assert value is None


@pytest.mark.asyncio
async def test_async_get(state_with_data):
    state, data = state_with_data
    with freeze_time("2023-01-14 12:00:00"):
        value = await state.async_get(data[0])
    assert value == data[1]


@pytest.mark.asyncio
async def test_async_get_without_ttl_set(state_with_data):
    state = TempFileState()
    data = [str(uuid4()), randint(1, 10), None]
    await state.async_set(*data)
    value = await state.async_get(data[0])
    assert value == data[1]
