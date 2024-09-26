def stage6(x):
    # sum = 0
    # bitmask = 2**16 - 1
    # solutions = [pow(i, -1 , 2**16 + 1) for i in [0xc0de, 0x0bad, 0x0510, 0x7149]]
    # for i in range(4):
    #     sum += ((((x & (bitmask * (2 ** (16*i)))) * solutions[i]) % ((2 ** 16 + 1) * 2**(16*i))) - 1)
    # return sum
    values = [int(('%.16x' % x)[4*i:4*i+4], 16) * pow(c, -1, 2**16 + 1) % (2**16 + 1) for i, c in enumerate([0x7149, 0x0510, 0x0bad, 0xc0de])]
    return sum((((v-1) % 2**16) * 2**(16*(3 - i)) for i, v in enumerate(values)))

print(stage6(0x714905100badc0de))
