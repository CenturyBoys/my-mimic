from dataclasses import dataclass

from mr_mime.states.type import StateType


@dataclass(slots=True, frozen=True)
class Config:
    type: StateType
    ttl: int = None
