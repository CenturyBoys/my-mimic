"""
Config for Mr Mime
"""

from dataclasses import dataclass
from typing import Type

from mr.states.interface import IState


@dataclass(slots=True, frozen=True)
class Config:
    """
    Config class
    """

    state: Type[IState]

    def __post_init__(self):
        if not issubclass(self.state, IState):
            raise TypeError("State class does not implement IState interface")
