"""Pure-python timing, linear scan vs binary search. No bisect, no list.index, fair fight."""
import random
import time

from search import binary_search


def linear_search(a, target):
    for i, v in enumerate(a):
        if v == target:
            return i
    return -1


def run_benchmark(n=200_000, q=50):
    a = [i * 2 for i in range(n)]  # evens only, so odd queries always miss
    rng = random.Random(73)
    qs = [rng.randrange(n * 2) for _ in range(q)]

    t = time.perf_counter()
    for x in qs:
        linear_search(a, x)
    lin = (time.perf_counter() - t) * 1000

    reps = 20  # binary is too quick to time once
    t = time.perf_counter()
    for _ in range(reps):
        for x in qs:
            binary_search(a, x)
    binary = (time.perf_counter() - t) * 1000 / reps

    return {"n": n, "queries": q, "linear_ms": round(lin, 2), "binary_ms": round(binary, 3)}
