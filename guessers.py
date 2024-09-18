import sys

def input_guesser(stage, wanted_output):
    return input("> ")

def list_guesser(it):
    it = iter(it)
    def guesser(stage, wanted_output):
        try:
            return next(it)
        except StopIteration:
            print("end of guess sequence", file=sys.stdout)
    return guesser