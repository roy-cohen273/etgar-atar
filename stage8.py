from decimal import Decimal

def stage8(x: Decimal) -> int:
    return int(str(x).replace('-', 'a').replace('.', 'c'), 13)
