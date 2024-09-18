from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, Any
import itertools

class SolvedLevel(ABC):
    @abstractmethod
    def solve(self, num) -> int: ...

@dataclass
class SolvedFunction(SolvedLevel):
    func: Callable[[int], Any]

    def solve(self, num):
        for i in itertools.count(0):
            if self.func(i) == num:
                return i
            if self.func(-i) == num:
                return -i


@dataclass
class SolvedInverse(SolvedLevel):
    func: Callable[[Any], int]

    def solve(self, num):
        return self.func(num)
