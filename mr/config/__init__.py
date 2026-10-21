"""
Config for Mr Mime
"""

from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from typing import Any

from mr.states.interface import IState


@dataclass(slots=True, frozen=True)
class Config:
    """
    Config class
    """

    state: type[IState]
    state_kwargs: dict[str, Any] = field(default_factory=dict)
    _state: IState | None = None

    def __post_init__(self) -> None:
        if not issubclass(self.state, IState):
            raise TypeError("State class does not implement IState interface")

    @property
    def initialized_state(self) -> IState:
        """
        Initialized state
        @return:
        """
        if self._state is None:
            state = self.state(**self.state_kwargs)
            object.__setattr__(self, "_state", state)
            return state
        return self._state

    @contextmanager
    def sync_acquire_state(self) -> Iterator[IState]:
        """
        Get sync state
        :return: IState
        """
        yield self.initialized_state

    @asynccontextmanager
    async def async_acquire_state(self) -> AsyncIterator[IState]:
        """
        Get async state
        :return: IState
        """
        yield self.initialized_state
