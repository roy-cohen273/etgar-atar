from typing import TypeAlias, Callable, Any
from tqdm import tqdm

import matplotlib.pyplot as plt
import IPython

Researcher: TypeAlias = Callable[[Callable[[int], int]], Any]

def list_researcher(guesses: list[int]) -> Researcher:
    def researcher(h: Callable[[int], int]) -> list[tuple[int, int]]:
        return list(zip(guesses, map(h, tqdm(guesses))))
    return researcher

def input_researcher(h: Callable[[int], int]) -> None:
    while True:
        guess = input("> ")
        if guess == "":
            break
        guess = int(guess)
        output = h(guess)
        print(f"h({guess}) = {output}")

# SECURITY WARNING: using eval_researcher gives you NRCE (non-remote code execution)
def eval_researcher(h: Callable[[int], int]) -> None:
    while True:
        expr = input("> ")
        if expr == "":
            break
        print(eval(expr, {'h': h}))

def ipython_researcher(h: Callable[[int], int]) -> None:
    IPython.start_ipython(user_ns={'h': h})

def aggregate_list_researcher(researcher: Researcher) -> Researcher:
    guesses = []
    outputs = []
    def my_researcher(h: Callable[[int], int]):
        def h_tag(guess: int) -> int:
            guesses.append(guess)
            output = h(guess)
            outputs.append(output)
            return output
        researcher_output = researcher(h_tag)
        return list(zip(guesses, outputs)), researcher_output
    return my_researcher

def plot_researcher(domain: list[int]) -> Researcher:
    def researcher(h: Callable[[int], int]) -> None:
        outputs = [h(x) for x in domain]
        plt.plot(domain, outputs, '.')
        plt.show()
    return researcher
