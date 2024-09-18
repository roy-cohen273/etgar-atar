def stage1(num: int) -> int:
    div, mod = divmod(num, 9)
    strAns = "9" * div
    strAns += str(mod)
    return int(strAns)