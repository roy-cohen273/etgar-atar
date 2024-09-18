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
from stage2 import stage2
from stage3 import stage3

solved_levels: list[SolvedLevel] = [
    SolvedInverse(stage0),
    SolvedInverse(stage1),
    SolvedInverse(stage2),
    SolvedInverse(stage3)
]

DATA_FILE = "data.json"
DEFAULT_GUESSER = input_guesser

def run(guesser: Callable[[int, str], int]) -> tuple[int, int, str]:
    proc = subprocess.Popen(["./etgar.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdin = proc.stdin
    stdout = proc.stdout

    while True:
        line = stdout.readline().strip(b'\n').decode()
        m: re.Match | None = re.match(r"^stage(\d+): h\(\?\) = ((\d+)|(\w*))$", line)
        if not m:
            print(f"line does not match regex: {line}", file=sys.stderr)

        stage = int(m.group(1))
        wanted_output = int(m.group(3)) if m.group(3) else m.group(4)

        if 0 <= stage < len(solved_levels):
            solution = solved_levels[stage].solve(wanted_output)
            # print(str(solution).encode(), file=stdin)
            stdin.write((str(solution) + "\n").encode())
            stdin.flush()
            line = stdout.readline().strip(b'\n').decode()
            if line != f">>> stage{stage} Concurred!":
                line = stdout.readline().strip(b'\n')
                print(
                    f"solution for stage {stage} failed!\nstage{stage}: h(?) = {wanted_output}\nhint: {line}"
                )
        else:
            print(f"stage {stage}. prompt: h(?) = {wanted_output}")
            guess = guesser(stage, wanted_output)
            stdin.write((str(guess) + "\n").encode())
            stdin.flush()
            line = stdout.readline().strip(b'\n').decode()
            if line == f">>> stage{stage} Concurred!":
                print("success!")
            elif line == ">>> Wrong answer, but I will be nice and give you a hint :)":
                line = stdout.readline().strip(b'\n').decode()
                print(line)
                m = re.match(r"^-> h\((\d+)\) = ((\d+)|(\w*))$", line)
                if not m:
                    print(f"hint line does not match regex: {line}")
                return stage, int(m.group(1)), int(m.group(3)) if m.group(3) else m.group(4)
            else:
                print(f"unknown line encountered: {line}")


def main():
    stages = []
    guesses = []
    outputs = []
    error = None
    while True:
        try:
            stage, guess, output = run(DEFAULT_GUESSER)
        except Exception as e:
            error = e
            raise
            break

        stages.append(stage)
        guesses.append(guess)
        outputs.append(output)

        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
        if str(stage) not in data:
            data[str(stage)] = {}
        data[str(stage)][str(guess)] = output
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)
    
    print(f"ERROR: {error}")
    print(list(zip(guesses, outputs)))


if __name__ == "__main__":
    main()
