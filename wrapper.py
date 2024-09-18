#!/usr/bin/env python3

import sys
import re
import subprocess
import json
from typing import Callable

from solved_level import SolvedFunction, SolvedInverse, SolvedLevel
from guessers import input_guesser, list_guesser
from stage0 import stage0
from stage1 import stage1

solved_levels: list[SolvedLevel] = [
    SolvedInverse(stage0),
    SolvedInverse(stage1),
]

DATA_FILE = "data.json"
DEFAULT_GUESSER = list_guesser(pow(2, i) for i in range(64))

def run(guesser: Callable[[int, int], int]):
    proc = subprocess.Popen(["./etgar.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdin = proc.stdin
    stdout = proc.stdout

    while True:
        line = stdout.readline().strip().decode()
        m: re.Match | None = re.match(r"^stage(\d+): h\(\?\) = (\d+)$", line)
        if not m:
            print(f"line does not match regex: {line}", file=sys.stderr)
        
        stage = int(m.group(1))
        wanted_output = int(m.group(2))

        if 0 <= stage < len(solved_levels):
            solution = solved_levels[stage].solve(wanted_output)
            # print(str(solution).encode(), file=stdin)
            stdin.write((str(solution) + '\n').encode())
            stdin.flush()
            line = stdout.readline().strip().decode()
            if line != f">>> stage{stage} Concurred!":
                print(f"solution for stage {stage} failed!\nstage{stage}: h(?) = {wanted_output}\nhint: {stdout.readline().strip()}")
        else:
            print(f"stage {stage}. prompt: h(?) = {wanted_output}")
            guess = guesser(stage, wanted_output)
            stdin.write((str(guess) + '\n').encode())
            stdin.flush()
            line = stdout.readline().strip().decode()
            if line == f">>> stage{stage} Concurred!":
                print("success!")
            elif line == ">>> Wrong answer, but I will be nice and give you a hint :)":
                line = stdout.readline().strip().decode()
                m = re.match(r"^-> h\((\d+)\) = (\d+)$", line)
                if m:
                    guess = int(m.group(1))
                    output = int(m.group(2))
                    with open(DATA_FILE, 'r') as f:
                        data = json.load(f)
                    if str(stage) not in data:
                        data[str(stage)] = {}
                    data[str(stage)][str(guess)] = output
                    with open(DATA_FILE, 'w') as f:
                        json.dump(data, f)
                print(line)
                break
            else:
                print(f"unknown line encountered: {line}")


def main():
    while True:
        run(DEFAULT_GUESSER)

if __name__ == '__main__':
    main()