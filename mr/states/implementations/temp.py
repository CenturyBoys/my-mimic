"""
Memory state implementation
"""
import pickle
import tempfile
from datetime import datetime
from inspect import _empty
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional

import aiofile

from mr.states.interface import IState


class TempFileState(IState):
    """
    State interface
    """

    _path: Path
    _temp_folder: TemporaryDirectory

    def __init__(self, **kwargs):
        try:
            _dir = Path(tempfile.gettempdir())
            if kwargs.get("BASE_PATH") is not None:
                _dir = Path(kwargs["BASE_PATH"])
            if kwargs.get("STATIC"):
                self._path = _dir
            else:
                self._temp_folder = TemporaryDirectory(  # pylint: disable=R1732
                    dir=_dir
                )
                self._path = Path(self._temp_folder.name)
        except (TypeError, FileNotFoundError, PermissionError) as exception:
            raise TypeError(
                "The config value BASE_PATH is not a valid Path"
            ) from exception

    def get_path(self, key: int) -> Path:
        """
        Get temp file path
        :return: Path
        """
        temp_path = self._path / str(key)
        return temp_path

    def sync_get(self, key: int):
        path = self.get_path(key=key)
        if path.exists():
            with open(path, "rb") as file:
                value = file.read()
            return self.__unpickle_with_header(value)
        return None

    def sync_set(self, key: int, value: any, ttl: int = _empty):
        path = self.get_path(key=key)
        with open(path, "wb") as file:
            file.write(self.__pickle_with_header(value, ttl))

    async def async_get(self, key: int):
        path = self.get_path(key=key)
        if path.exists():
            async with aiofile.async_open(path, "rb") as file:
                value = await file.read()
            return self.__unpickle_with_header(value)
        return None

    async def async_set(self, key: int, value: any, ttl: int = _empty):
        path = self.get_path(key=key)
        async with aiofile.async_open(path, "wb") as file:
            await file.write(self.__pickle_with_header(value, ttl))

    @staticmethod
    def __pickle_with_header(value: any, ttl: int = _empty) -> bytes:
        pack = {
            "created_at": datetime.utcnow().timestamp(),
            "ttl": ttl,
            "value": pickle.dumps(value),
        }
        return pickle.dumps(pack)

    @staticmethod
    def __unpickle_with_header(pack_bytes: bytes) -> Optional[any]:
        now_timestamp = datetime.utcnow().timestamp()
        pack = pickle.loads(pack_bytes)
        register_timestamp = pack.get("created_at")
        _ttl = pack.get("ttl")
        if _ttl == _empty or ((register_timestamp + _ttl) >= now_timestamp):
            return pickle.loads(pack.get("value"))
        return None
