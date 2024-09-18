#!/usr/bin/env python3

import sys
import re
import subprocess
import json
import socket

from solved_level import SolvedFunction, SolvedInverse, SolvedLevel
from researcher import Researcher, aggregate_list_researcher, input_researcher, list_researcher, plot_researcher, eval_researcher
from stage0 import stage0
from stage1 import stage1
from stage2 import stage2
from stage3 import stage3
from stage4 import stage4

solved_levels: list[SolvedLevel] = [
    SolvedInverse(stage0),
    SolvedInverse(stage1),
    SolvedInverse(stage2),
    SolvedInverse(stage3),
    SolvedInverse(stage4),
]

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5038
DATA_FILE = "data.json"
DEFAULT_RESEARCHER = aggregate_list_researcher(input_researcher)
# DEFAULT_RESEARCHER = list_researcher(range(1_000_000))
# DEFAULT_RESEARCHER = plot_researcher(list(range(100)))
# DEFAULT_RESEARCHER = aggregate_list_researcher(eval_researcher)

def run(guess: int) -> tuple[int, int, int]:
    with subprocess.Popen(["./etgar.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as proc:
        stdin = proc.stdin
        stdout = proc.stdout

        def get_line() -> str:
            return stdout.readline().decode().strip('\r\n')
        
        def send_guess(guess: int) -> None:
            stdin.write(str(guess).encode() + b'\n')
            stdin.flush()

        while True:
            line = get_line()
            m: re.Match | None = re.match(r"^stage(\d+): h\(\?\) = ((\d+)|(\w*))$", line)
            if not m:
                print(f"line does not match regex: {line}", file=sys.stderr)

            stage = int(m.group(1))
            wanted_output = int(m.group(3)) if m.group(3) else m.group(4)

            if 0 <= stage < len(solved_levels):
                solution = solved_levels[stage].solve(wanted_output)
                # print(str(solution), file=stdin)
                send_guess(solution)
                line = get_line()
                if line != f">>> stage{stage} Concurred!":
                    line = get_line()
                    print(
                        f"solution for stage {stage} failed!\nstage{stage}: h(?) = {wanted_output}\nhint: {line}"
                    )
            else:
                # print(f"stage {stage}. prompt: h(?) = {wanted_output}")
                send_guess(guess)
                line = get_line()
                if line == f">>> stage{stage} Concurred!":
                    print("success!")
                elif line == ">>> Wrong answer, but I will be nice and give you a hint :)":
                    line = get_line()
                    # print(line)
                    m = re.match(r"^-> h\((\d+)\) = ((\d+)|(\w*))$", line)
                    if not m:
                        print(f"hint line does not match regex: {line}")
                    return stage, int(m.group(1)), int(m.group(3)) if m.group(3) else m.group(4)
                else:
                    print(f"unknown line encountered: {line}")

def research(researcher: Researcher):
    def h(guess: int) -> int:
        stage, guess2, output = run(guess)
        if guess != guess2:
            print(f"given guess: {guess}, answered guess: {guess2}", file=sys.stderr)
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        if str(stage) not in data:
            data[str(stage)] = {}
        data[str(stage)][str(guess)] = output
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        return output

    return researcher(h)

def main():
    # proc = subprocess.Popen(["./etgar.py", "serv"])
    print(research(DEFAULT_RESEARCHER))
    # proc.kill()


if __name__ == "__main__":
    main()
