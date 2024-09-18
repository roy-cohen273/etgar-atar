from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable
import itertools

class SolvedLevel(ABC):
    @abstractmethod
    def solve(self, num): ...

@dataclass
class SolvedFunction(SolvedLevel):
    func: Callable[[int], int]

    def solve(self, num):
        for i in itertools.count(0):
            if self.func(i) == num:
                return i
            if self.func(-i) == num:
                return -i


@dataclass
class SolvedInverse(SolvedLevel):
    func: Callable[[int], int]

    def solve(self, num):
        return self.func(num)
