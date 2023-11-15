"""
Config for Mr Mime
"""
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import Type

from mr.states.interface import IState


@dataclass(slots=True, frozen=True)
class Config:
    """
    Config class
    """

    state: Type[IState]
    state_kwargs: dict = field(default_factory=dict)
    _state: IState = None

    def __post_init__(self):
        if not issubclass(self.state, IState):
            raise TypeError("State class does not implement IState interface")

    @property
    def initialized_state(self):
        """
        Initialized sate
        @return:
        """
        if self._state is None:
            object.__setattr__(self, "_state", self.state(**self.state_kwargs))
        return self._state

    @contextmanager
    def sync_acquire_state(self) -> IState:
        """
        Get sync state
        :return: SyncRedis
        """
        yield self.initialized_state

    @asynccontextmanager
    async def async_acquire_state(self) -> IState:
        """
        Get sync state
        :return: SyncRedis
        """
        yield self.initialized_state
