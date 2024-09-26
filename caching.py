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
            with open(self.FILENAME_FORMAT.format(self=self), 'r' + self.FILE_TYPE) as f:
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


class SeekCache(Cache, filename_format="seek_cache_stage{self.stage}.data"):
    # The cache is a HUGE list of entries. Each entry consists of a pair (tag, output).
    # The size of the file will not exceed 2^32 bytes, because seeking to very large offsets fails.
    # |output| = 8 bytes, since we're assuming the output will be in the range [0, 2^64).
    # 
    # Our constraints are:
    # 1. |entry| >= |tag| + |output| = |tag| + 8
    # 2. #entries <= 2^32 / |entry|
    # 3. #colisions >= 2^64 / #entries
    # 4. 8 * |tag| >= log2(#colisions)
    #
    # The smallest |tag| that can satisfy those constraints is ~4.45.
    # Therefore, we'll use an 8-byte tag. That means each entry will be 16 bytes long, and there will be 2^28 entries.
    #
    # The cache is organized as a (2^N)-way cache.
    # That means the enrties are divided to 2^N ways, and each way has 2^(28-N) entries.

    N = 3  # 8-way cache

    TAG_STRUCT_FORMAT = "<Q"
    TAG_SIZE = struct.calcsize(TAG_STRUCT_FORMAT)

    OUTPUT_STRUCT_FORMAT = "<Q"
    OUTPUT_SIZE = struct.calcsize(OUTPUT_STRUCT_FORMAT)

    ENTRY_STRUCT_FORMAT = TAG_STRUCT_FORMAT + OUTPUT_STRUCT_FORMAT
    # ENTRY_SIZE = struct.calcsize(ENTRY_STRUCT_FORMAT)
    ENTRY_SIZE = struct.calcsize("<QQ")
    
    def __enter__(self):
        self.f = open(self.filename, 'r+b')
        self.f.__enter__()
        return super().__enter__()
    
    def __exit__(self, exc_type, exc_value, traceback):
        return self.f.__exit__(exc_type, exc_value, traceback)
    
    def seek(self, guess: int) -> Iterable[None]:
        # reduce guess modulo 2^(28-N) 
        guess &= (1 << (28 - self.N)) - 1

        for i in range(1 << self.N):
            self.f.seek(guess * self.ENTRY_SIZE + i << (28 - self.N))
            yield None
        
        # seek to the appropriate entry in the file
        # self.f.seek(guess * self.ENTRY_SIZE)

    def search(self, guess: int) -> int | None:
        for _ in self.seek(guess):
            entry = self.f.read(self.ENTRY_SIZE)
            if len(entry) != self.ENTRY_SIZE:
                break  # found empty entry
            
            tag, output = struct.unpack(self.ENTRY_STRUCT_FORMAT, entry)
            
            if output == 0:
                break  # found empty entry

            if tag != guess:
                continue  # found occupied entry
            
            return output
        
        return None
    
    def update(self, guess: int, output: int) -> None:
        # check that output is in range
        if output <= 0 or output >= 1 << (self.OUTPUT_SIZE * 8):
            return
        
        # search for an empty entry, break when finding one
        for _ in self.seek(guess):
            tag = self.f.read(self.TAG_SIZE)
            if len(tag) != self.TAG_SIZE:
                break

            data = struct.pack(self.OUTPUT_STRUCT_FORMAT, output)
            self.f.write(data)
