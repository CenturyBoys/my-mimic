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
    kwargs: dict = field(default_factory=dict)
    _state: IState = None

    def __post_init__(self):
        if not issubclass(self.state, IState):
            raise TypeError("State class does not implement IState interface")
        self.__init_state()

    def __init_state(self):
        object.__setattr__(self, "_state", self.state(**self.kwargs))

    @contextmanager
    def sync_acquire_state(self) -> IState:
        yield self._state

    @asynccontextmanager
    async def async_acquire_state(self) -> IState:
        yield self._state
