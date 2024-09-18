from math import log2

data = {
    "1": 281474976710656,
    "2": 2251799813685248,
    "4": 67108864,
    "8": 144115188075855872,
    "16": 9223372036854775808,
    "32": 4294967296,
    "64": 32768,
    "128": 68719476736,
    "256": 549755813888,
    "512": 35184372088832,
    "1024": 2097152,
    "2048": 1,
    "4096": 288230376151711744,
    "8192": 70368744177664,
    "16384": 8,
    "32768": 18014398509481984,
    "65536": 32,
    "131072": 1073741824,
    "262144": 137438953472,
    "524288": 4096,
    "1048576": 524288,
    "2097152": 2305843009213693952,
    "4194304": 8388608,
    "8388608": 64,
    "16777216": 4,
    "33554432": 268435456,
    "67108864": 8192,
    "134217728": 576460752303423488,
    "268435456": 4503599627370496,
    "536870912": 1152921504606846976,
    "1073741824": 16,
    "2147483648": 2199023255552,
    "4294967296": 562949953421312,
    "8589934592": 17179869184,
    "17179869184": 134217728,
    "34359738368": 140737488355328,
    "68719476736": 131072,
    "137438953472": 17592186044416,
    "274877906944": 256,
    "549755813888": 34359738368,
    "1099511627776": 65536,
    "2199023255552": 1024,
    "4398046511104": 128,
    "8796093022208": 4194304,
    "17592186044416": 2147483648,
    "35184372088832": 512,
    "70368744177664": 4611686018427387904,
    "140737488355328": 2,
    "281474976710656": 262144,
    "562949953421312": 274877906944,
    "1125899906842624": 72057594037927936,
    "2251799813685248": 9007199254740992,
    "4503599627370496": 1125899906842624,
    "9007199254740992": 1099511627776,
    "18014398509481984": 36028797018963968,
    "36028797018963968": 2048,
    "72057594037927936": 16777216,
    "144115188075855872": 8589934592,
    "288230376151711744": 16384,
    "576460752303423488": 4398046511104,
    "1152921504606846976": 33554432,
    "2305843009213693952": 8796093022208,
    "4611686018427387904": 1048576,
    "9223372036854775808": 536870912,
}

size = 64

sol = {val: int(index) for index, val in data.items()}
# print(sol)
logSol = {int(log2(x)): int(log2(y)) for x, y in sol.items()}
# print(logSol)

inversePerm = {
    48: 0,
    51: 1,
    26: 2,
    57: 3,
    63: 4,
    32: 5,
    15: 6,
    36: 7,
    39: 8,
    45: 9,
    21: 10,
    0: 11,
    58: 12,
    46: 13,
    3: 14,
    54: 15,
    5: 16,
    30: 17,
    37: 18,
    12: 19,
    19: 20,
    61: 21,
    23: 22,
    6: 23,
    2: 24,
    28: 25,
    13: 26,
    59: 27,
    52: 28,
    60: 29,
    4: 30,
    41: 31,
    49: 32,
    34: 33,
    27: 34,
    47: 35,
    17: 36,
    44: 37,
    8: 38,
    35: 39,
    16: 40,
    10: 41,
    7: 42,
    22: 43,
    31: 44,
    9: 45,
    62: 46,
    1: 47,
    18: 48,
    38: 49,
    56: 50,
    53: 51,
    50: 52,
    40: 53,
    55: 54,
    11: 55,
    24: 56,
    33: 57,
    14: 58,
    42: 59,
    25: 60,
    43: 61,
    20: 62,
    29: 63,
}


def stage2(x):
    r = 0
    for i in range(64):
        if x % 2 == 1:
            r += 2 ** inversePerm[i]
        x //= 2
    return r