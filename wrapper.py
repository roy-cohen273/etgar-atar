#!/usr/bin/env python3

import sys
import re
import subprocess

from solved_level import SolvedFunction, SolvedInverse, SolvedLevel
from stage0 import stage0
from stage1 import stage1

solved_levels: list[SolvedLevel] = [
    SolvedInverse(stage0),
    SolvedInverse(stage1),
]

def main():
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

if __name__ == '__main__':
    main()