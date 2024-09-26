#!/usr/bin/env python3

import sys
import re
import subprocess
import json
import socket

from solved_level import SolvedFunction, SolvedInverse, SolvedLevel
from researcher import (
    Researcher, aggregate_list_researcher, input_researcher, list_researcher,
    plot_researcher, eval_researcher, ipython_researcher
)
from caching import JsonCache, PickleCache
from stage0 import stage0
from stage1 import stage1
from stage2 import stage2
from stage3 import stage3
from stage4 import stage4
from stage5 import stage5
from stage6 import stage6
from stage7 import stage7

solved_levels: list[SolvedLevel] = [
    SolvedInverse(stage0),
    SolvedInverse(stage1),
    SolvedInverse(stage2),
    SolvedInverse(stage3),
    SolvedInverse(stage4),
    SolvedInverse(stage5),
    SolvedInverse(stage6),
    SolvedInverse(stage7),
]

DATA_FILE = "data.json"
# DEFAULT_RESEARCHER = aggregate_list_researcher(input_researcher)
# DEFAULT_RESEARCHER = list_researcher([2** i for i in range(64)])
# DEFAULT_RESEARCHER = plot_researcher(list(range(20))
# DEFAULT_RESEARCHER = aggregate_list_researcher(eval_researcher)
DEFAULT_RESEARCHER = aggregate_list_researcher(ipython_researcher)

DEFAULT_CACHE = JsonCache

def parse_output(output: str):
    try:
        return int(output)
    except ValueError:
        pass
    try:
        return float(output)
    except ValueError:
        pass
    return output

def run(guess: int) -> tuple[int, int, int]:
    while True:
        with subprocess.Popen(["./etgar.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as proc:
            def get_line() -> str:
                return proc.stdout.readline().decode().strip('\r\n')
            
            def send_guess(guess: int) -> None:
                proc.stdin.write(str(guess).encode() + b'\n')
                proc.stdin.flush()

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
                print("tage does not match solved_levels list")
                return 0

            cache.update(guess, output)

            # with open(DATA_FILE, 'r') as f:
            #     data = json.load(f)
            # if str(stage) not in data:
            #     data[str(stage)] = {}
            # data[str(stage)][str(guess)] = output
            # with open(DATA_FILE, 'w') as f:
            #     json.dump(data, f, indent=4)

            return output

        return researcher(h)

def main():
    # proc = subprocess.Popen(["./etgar.py", "serv"])
    print(research(DEFAULT_RESEARCHER))
    # proc.kill()


if __name__ == "__main__":
    main()
