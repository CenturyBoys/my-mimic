from mr_mime.config import Config
from mr_mime.states.implements.memory import MemoryState
from mr_mime.states.interface import IState
from mr_mime.states.type import StateType


class StateFactory:

    @staticmethod
    def get_state(config: Config) -> IState:
        if config.type == StateType.MEMORY:
            return MemoryState()
