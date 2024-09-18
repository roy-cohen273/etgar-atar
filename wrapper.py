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
    proc = subprocess.Popen(["etgar.py"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdin = proc.stdin
    stdout = proc.stdout

    while True:
        line = stdin.readline().strip()
        m: re.Match = re.match(r"^stage(\d+): h\(\?\) = (\d+)$", line)
        if not m:
            print(f"line does not match regex: {line}", file=sys.stderr)
        
        stage = int(m.group(1))
        wanted_output = int(m.group(2))

        if 0 <= stage < len(solved_levels):
            solution = solved_levels[stage].solve(wanted_output)
            print(solution, file=stdout)

if __name__ == '__main__':
    main()