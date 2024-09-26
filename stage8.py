def stage8(x: float) -> int:
    return int(str(x).replace('-', 'a').replace('.', 'c'), 13)
