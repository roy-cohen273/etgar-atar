#!/usr/bin/env python3

import sys
import re
import socket
import decimal
from decimal import Decimal

from solved_level import SolvedFunction, SolvedInverse, SolvedLevel
from researcher import (
    Researcher, aggregate_list_researcher, input_researcher, list_researcher,
    plot_researcher, eval_researcher, ipython_researcher
)
from caching import NoCache, JsonCache, PickleCache
from stage0 import stage0
from stage1 import stage1
from stage2 import stage2
from stage3 import stage3
from stage4 import stage4
from stage5 import stage5
from stage6 import stage6
from stage7 import stage7_old
from stage8 import stage8

solved_levels: list[SolvedLevel] = [
    SolvedInverse(stage0),
    SolvedInverse(stage1),
    SolvedInverse(stage2),
    SolvedInverse(stage3),
    SolvedInverse(stage4),
    SolvedInverse(stage5),
    SolvedInverse(stage6),
    SolvedInverse(stage7_old),
    SolvedInverse(stage8),
]

DATA_FILE = "data.json"
# DEFAULT_RESEARCHER = aggregate_list_researcher(input_researcher)
# DEFAULT_RESEARCHER = list_researcher([2** i for i in range(64)])
# DEFAULT_RESEARCHER = plot_researcher(range(6*1<<61, (6*1<<61)+20))
# DEFAULT_RESEARCHER = aggregate_list_researcher(eval_researcher)
# DEFAULT_RESEARCHER = aggregate_list_researcher(ipython_researcher)
DEFAULT_RESEARCHER = ipython_researcher

DEFAULT_CACHE = NoCache

def parse_output(output: str):
    try:
        return int(output)
    except ValueError:
        pass
    try:
        return Decimal(output)
    except decimal.InvalidOperation:
        pass
    return output

def run(guess: int) -> tuple[int, int, int]:
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(('server.do.daarazimfree.com', 4444))

            stdin = open(sock.fileno(), 'wb', closefd=False)
            stdout = open(sock.fileno(), 'rb', closefd=False)

            def get_line() -> str:
                return stdout.readline().decode().strip('\r\n')
            
            def send_guess(guess: int) -> None:
                stdin.write(str(guess).encode() + b'\n')
                stdin.flush()

            while True:
                line = get_line()
                m: re.Match | None = re.match(r"^stage(\d+): h\(\?\) = (.*)$", line)
                if not m:
                    print(f"line does not match regex: {line}", file=sys.stderr)

                stage = int(m.group(1))
                wanted_output = parse_output(m.group(2))

                if 0 <= stage < len(solved_levels):
                    solution = solved_levels[stage].solve(wanted_output)
                    send_guess(solution)
                    line = get_line()
                    if line != f">>> stage{stage} Concurred!":
                        line = get_line()
                        print(
                            f"solution for stage {stage} failed!\nstage{stage}: h(?) = {wanted_output}\nhint: {line}"
                        )
                        break
                else:
                    # print(f"stage {stage}. prompt: h(?) = {wanted_output}")
                    send_guess(guess)
                    line = get_line()
                    if line == f">>> stage{stage} Concurred!":
                        print("success!")
                    elif line == ">>> Wrong answer, but I will be nice and give you a hint :)":
                        line = get_line()
                        # print(line)
                        m = re.match(r"^-> h\((\d+)\) = (.*)$", line)
                        if not m:
                            print(f"hint line does not match regex: {line}")
                        return stage, int(m.group(1)), parse_output(m.group(2))
                    else:
                        print(f"unknown line encountered: {line}")

def research(researcher: Researcher):
    with DEFAULT_CACHE(len(solved_levels)) as cache:
        def h(guess: int) -> int:
            cached = cache.search(guess)
            if cached is not None:
                return cached

            stage, guess2, output = run(guess)
            if guess != guess2:
                print(f"given guess: {guess}, answered guess: {guess2}", file=sys.stderr)
            if stage != len(solved_levels):
                print("stage does not match solved_levels list")
                return 0

            cache.update(guess, output)

            return output

        return researcher(h)

def main():
    print(research(DEFAULT_RESEARCHER))


if __name__ == "__main__":
    main()
