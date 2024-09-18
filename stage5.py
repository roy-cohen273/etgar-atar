def h(i: int) -> int:
    return (8836 * pow(12472, i, (1 << 16) + 1)) % ((1 << 16) + 1)

values = [0] * (1 << 16)
for i in range(1 << 16):
    values[h(i) - 1] = i

def stage5(num: int) -> int:
    return values[(num & ((1 << 16) - 1)) - 1]
