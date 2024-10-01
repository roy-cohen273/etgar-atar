import os
from datetime import datetime, timedelta
from abc import ABC, ABCMeta, abstractmethod
import json, pickle
import struct
from typing import Iterable

class Cache(ABC):
    def __init_subclass__(cls, /, filename_format: str, **kwargs) -> None:
        super().__init_subclass__(**kwargs)

        cls.FILENAME_FORMAT = filename_format

    def __init__(self, stage: int):
        self.stage = stage
        self.filename = "caches/" + self.FILENAME_FORMAT.format(self=self)
    
    @abstractmethod
    def __enter__(self):
        return self
    
    @abstractmethod
    def __exit__(self, exc_type, exc_value, traceback):
        return False

    @abstractmethod
    def search(self, guess: int) -> int | None: ...

    @abstractmethod
    def update(self, guess: int, output: int) -> None: ...

class NoCache(Cache, filename_format=""):
    def __enter__(self):
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        return super().__exit__(exc_type, exc_value, traceback)

    def search(self, guess: int) -> int | None:
        return None
    
    def update(self, guess: int, output: int) -> None:
        pass

class SerializationCache(Cache, filename_format=""):
    SYNC_INTERVAL = timedelta(seconds=1)

    def __init_subclass__(cls, /, extension: str, is_binary: bool, **kwargs) -> None:
        super().__init_subclass__(filename_format=f"serialization_cache_stage{{self.stage}}.{extension}", **kwargs)

        cls.FILE_EXTENSION = extension
        cls.FILE_TYPE = 'b' if is_binary else 't'
    
    @classmethod
    @abstractmethod
    def serialize(cls, obj, f) -> None: ...

    @classmethod
    @abstractmethod
    def deserialize(cls, f): ...

    def __init__(self, stage: int):
        super().__init__(stage)
        self.dict = {}
        self.last_sync = datetime.fromtimestamp(0)
        self.dirty = False

    def sync(self):
        if os.path.getmtime(self.filename) > self.last_sync.timestamp():
            # the file has been modified since last sync
            with open(self.filename, 'r' + self.FILE_TYPE) as f:
                dict2 = self.deserialize(f)
    
            self.dict.update(dict2)
            if not self.dirty and self.dict != dict2:
                self.dirty = True        

        if self.dirty:
            with open(self.filename, 'w' + self.FILE_TYPE) as f:
                self.serialize(self.dict, f)
            
            self.dirty = False

        self.last_sync = datetime.now()
    
    def __enter__(self):
        if not os.path.exists(self.filename):
            with open(self.filename, 'w' + self.FILE_TYPE) as f:
                self.serialize({}, f)
        
        self.sync()

        return super().__enter__()
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.sync()
        return super().__exit__(exc_type, exc_value, traceback)
    
    def search(self, guess: int) -> int | None:
        if datetime.now() - self.last_sync >= self.SYNC_INTERVAL:
            self.sync()

        return self.dict.get(guess, None)
    
    def update(self, guess: int, output: int) -> None:
        if datetime.now() - self.last_sync >= self.SYNC_INTERVAL:
            self.sync()

        if guess not in self.dict:
            self.dict[guess] = output
            self.dirty = True


class JsonCache(SerializationCache, extension='json', is_binary=False):
    @classmethod
    def serialize(cls, obj, f) -> None:
        json.dump(obj, f, indent=4)

    @classmethod
    def deserialize(cls, f):
        return json.load(f, object_pairs_hook=lambda pairs: {int(k): v for k, v in pairs})


class PickleCache(SerializationCache, extension='pickle', is_binary=True):
    @classmethod
    def serialize(cls, obj, f) -> None:
        pickle.dump(obj, f)

    @classmethod
    def deserialize(cls, f):
        return pickle.load(f)
