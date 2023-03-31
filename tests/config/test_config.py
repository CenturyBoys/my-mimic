import pytest

from mr import Config, IState


def test_config_error():
    class T1:
        pass

    with pytest.raises(TypeError) as error:
        Config(state=T1)
    assert error.value.args == ("State class does not implement IState interface",)


class StubState(IState):
    def sync_get(self, key: str):
        pass

    def sync_set(self, key: str, value: any, ttl: int = None):
        pass

    async def async_get(self, key: str):
        pass

    async def async_set(self, key: str, value: any, ttl: int = None):
        pass


def test_config():

    config = Config(state=StubState)
    assert issubclass(config.state, StubState)
