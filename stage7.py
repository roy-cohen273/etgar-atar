from math import factorial

def n_choose_k(n, k):
    prod = 1
    for i in range(k):
        if (i < n):
            prod = prod * (n - i)
    return prod // factorial(k)

def inverse_inverse(guess):
    return sum([n_choose_k(guess - 1, i) for i in range(5)])

def stage7_checker(guess, target):
    return inverse_inverse(guess) == target

def stage7_old(x):
    initial_guess = int((x * 24)**0.25)
    guesses = [initial_guess + i for i in range (1000)] + [initial_guess - i for i in range(1000)]
    for guess in guesses:
        if stage7_checker(guess, x):
            return guess 
    return initial_guess

def stage7_binary_search(start, end, target):
    # should be better but does not work currently
    if (end - start) < 5:
        for guess in range(start, end + 1):
            if stage7_checker(guess, target):
                return guess
    middle = (start + end) // 2
    h_of_middle = inverse_inverse(middle)
    if h_of_middle == target:
        return middle
    if h_of_middle < target:
        return stage7_binary_search(middle, end, target)
    return stage7_binary_search(start, middle, target)
    
def stage7(x):
    initial_guess  = int((x * 24)**0.25)
    stage7_binary_search(initial_guess - 2000, initial_guess + 2000, x)


 