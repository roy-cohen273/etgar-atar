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

def stage7(x):
    initial_guess = int((x * 24)**0.25)
    guesses = [initial_guess + i for i in range (1000)] + [initial_guess - i for i in range(1000)]
    for guess in guesses:
        if stage7_checker(guess, x):
            return guess 
    return initial_guess


if __name__ == "__main__":
    print([inverse_inverse(2**i) for i in range(64)])