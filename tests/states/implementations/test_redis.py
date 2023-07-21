import pickle
from unittest.mock import patch, MagicMock, AsyncMock
import pytest
from redis.asyncio.client import Redis as AsyncRedis
from redis.client import Redis as SyncRedis

from mr.states import RedisState


def test_missing_config():
    with pytest.raises(KeyError) as exception:
        RedisState()
    assert exception.value.args[0] == "The config value REDIS_URL was not informed"


def test_sync_state():
    state = RedisState(REDIS_URL="redis://")
    mock_object = MagicMock()
    with patch.object(SyncRedis, "from_url", return_value=mock_object):
        state.sync_set("t1", 10, 1)
        state.sync_set("t1", 10, 1)
    assert mock_object.set.call_count == 2


@pytest.mark.asyncio
async def test_async_state():
    state = RedisState(REDIS_URL="redis://")
    mock_object = AsyncMock()
    with patch.object(AsyncRedis, "from_url", return_value=mock_object):
        await state.async_set("t1", 10, 1)
        await state.async_set("t1", 10, 1)
    assert mock_object.set.call_count == 2


def test_sync_set():
    state = RedisState(REDIS_URL="redis://")
    mock_object = MagicMock()
    with patch.object(SyncRedis, "from_url", return_value=mock_object):
        state.sync_set("t1", 10, 1)
    mock_object.set.assert_called_once()


@pytest.mark.asyncio
async def test_async_set():
    state = RedisState(REDIS_URL="redis://")
    mock_object = AsyncMock()
    with patch.object(AsyncRedis, "from_url", return_value=mock_object):
        await state.async_set("t1", 10, 1)
    mock_object.set.assert_called_once()


def test_sync_get_none():
    state = RedisState(REDIS_URL="redis://")
    mock_object = MagicMock()
    mock_object.get.return_value = None
    with patch.object(SyncRedis, "from_url", return_value=mock_object):
        value = state.sync_get("t1")
    assert value is None
    mock_object.get.assert_called_once()


@pytest.mark.asyncio
async def test_async_get_none():
    state = RedisState(REDIS_URL="redis://")
    mock_object = AsyncMock()
    mock_object.get.return_value = None
    with patch.object(AsyncRedis, "from_url", return_value=mock_object):
        value = await state.async_get("t1")
    assert value is None
    mock_object.get.assert_called_once()


def test_sync_get():
    state = RedisState(REDIS_URL="redis://")
    mock_object = MagicMock()
    mock_object.get.return_value = pickle.dumps(1)
    with patch.object(SyncRedis, "from_url", return_value=mock_object):
        value = state.sync_get("t1")
    assert value == 1
    mock_object.get.assert_called_once()


@pytest.mark.asyncio
async def test_async_get():
    state = RedisState(REDIS_URL="redis://")
    mock_object = AsyncMock()
    mock_object.get.return_value = pickle.dumps(1)
    with patch.object(AsyncRedis, "from_url", return_value=mock_object):
        value = await state.async_get("t1")
    assert value == 1
    mock_object.get.assert_called_once()
