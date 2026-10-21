"""
Temp file state implementation
"""

import os
import pickle
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import aiofile

from mr.states.interface import NO_TTL, IState, Ttl

#: Pickle protocol pinned so the on-disk format stays stable across Python versions.
_PICKLE_PROTOCOL = 4


class TempFileState(IState):
    """
    State that persists cached returns to temp files
    """

    _path: Path
    _temp_folder: TemporaryDirectory[str]

    def __init__(self, **kwargs: Any) -> None:
        try:
            _dir = Path(tempfile.gettempdir())
            if kwargs.get("BASE_PATH") is not None:
                _dir = Path(kwargs["BASE_PATH"])
            if kwargs.get("STATIC"):
                self._path = _dir
            else:
                self._temp_folder = TemporaryDirectory(dir=_dir)
                self._path = Path(self._temp_folder.name)
        except (TypeError, FileNotFoundError, PermissionError) as exception:
            raise TypeError(
                "The config value BASE_PATH is not a valid Path"
            ) from exception

    def get_path(self, key: str) -> Path:
        """
        Get temp file path
        :return: Path
        """
        temp_path = self._path / str(key)
        return temp_path

    def sync_get(self, key: str) -> Any:
        path = self.get_path(key=key)
        if path.exists():
            with open(path, "rb") as file:
                value = file.read()
            return self.__unpickle_with_header(value)
        return None

    def sync_unset(self, key: str) -> None:
        path = self.get_path(key=key)
        if path.exists():
            os.remove(path)
        return None

    def sync_set(self, key: str, value: Any, ttl: Ttl = NO_TTL) -> None:
        path = self.get_path(key=key)
        with open(path, "wb") as file:
            file.write(self.__pickle_with_header(value, ttl))

    async def async_get(self, key: str) -> Any:
        path = self.get_path(key=key)
        if path.exists():
            async with aiofile.async_open(path, "rb") as file:
                value = await file.read()
            return self.__unpickle_with_header(value)
        return None

    async def async_set(self, key: str, value: Any, ttl: Ttl = NO_TTL) -> None:
        path = self.get_path(key=key)
        async with aiofile.async_open(path, "wb") as file:
            await file.write(self.__pickle_with_header(value, ttl))

    async def async_unset(self, key: str) -> None:
        self.sync_unset(key)
        return None

    @staticmethod
    def __pickle_with_header(value: Any, ttl: Ttl = NO_TTL) -> bytes:
        pack = {
            "created_at": datetime.now(timezone.utc).timestamp(),
            "ttl": ttl,
            "value": pickle.dumps(value, protocol=_PICKLE_PROTOCOL),
        }
        return pickle.dumps(pack, protocol=_PICKLE_PROTOCOL)

    @staticmethod
    def __unpickle_with_header(pack_bytes: bytes) -> Any:
        now_timestamp = datetime.now(timezone.utc).timestamp()
        pack = pickle.loads(pack_bytes)
        register_timestamp = pack.get("created_at")
        _ttl = pack.get("ttl")
        if _ttl == NO_TTL or ((register_timestamp + _ttl) >= now_timestamp):
            return pickle.loads(pack.get("value"))
        return None
