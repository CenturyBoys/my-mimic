import dataclasses

import pytest

from mr import Config, IState


def test_config_error():
    class T1:
        pass

    with pytest.raises(TypeError) as error:
        Config(state=T1)
    assert error.value.args == ("State class does not implement IState interface",)


class StubState(IState):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def sync_get(self, key: str):
        pass

    def sync_set(self, key: str, value: any, ttl: int = None):
        pass

    async def async_get(self, key: str):
        pass

    async def async_set(self, key: str, value: any, ttl: int = None):
        pass


def test_slots():
    config = Config(state=StubState, state_kwargs={"key": "value"})
    assert config.__slots__ == ("state", "state_kwargs", "_state")


def test_frozen():
    config = Config(state=StubState, state_kwargs={"key": "value"})
    with pytest.raises(dataclasses.FrozenInstanceError):
        config.state_kwargs = {}


def test_config():
    kwargs = {"key": "value"}
    config = Config(state=StubState, state_kwargs=kwargs)
    assert issubclass(config.state, StubState)
    assert config._state is None
    assert isinstance(config.initialized_state, StubState)
    assert config.state_kwargs == kwargs
