"""Benchmarks comparing Heapsort against Quicksort, Mergesort, and Python's sorted().

This script uses small default sizes for quick smoke tests. Use larger sizes for full experiments.
"""
import random
import time
import csv
import sys
from heapsort import heapsort


def quicksort(arr):
    if len(arr) <= 1:
        return arr[:]
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)


def mergesort(arr):
    if len(arr) <= 1:
        return arr[:]
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    res = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            res.append(left[i]); i += 1
        else:
            res.append(right[j]); j += 1
    res.extend(left[i:]); res.extend(right[j:])
    return res


def time_fn(fn, data):
    start = time.perf_counter()
    fn(list(data))
    return time.perf_counter() - start


def run_benchmarks(sizes=(100, 500), trials=3):
    kinds = ["random", "sorted", "reversed"]
    rows = []
    for n in sizes:
        for kind in kinds:
            for t in range(trials):
                if kind == "random":
                    data = [random.randint(0, n) for _ in range(n)]
                elif kind == "sorted":
                    data = list(range(n))
                else:
                    data = list(range(n, 0, -1))

                times = {"n": n, "kind": kind, "trial": t}
                times["heapsort"] = time_fn(heapsort, data)
                times["quicksort"] = time_fn(quicksort, data)
                times["mergesort"] = time_fn(mergesort, data)
                times["py_sorted"] = time_fn(sorted, data)
                print(f"n={n} kind={kind} trial={t} ->", times)
                rows.append(times)

    with open("sorting_benchmarks.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["n", "kind", "trial", "heapsort", "quicksort", "mergesort", "py_sorted"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


if __name__ == "__main__":
    # allow sizes override via CLI: e.g. `python benchmarks.py 100 500`
    if len(sys.argv) >= 3:
        sizes = tuple(int(x) for x in sys.argv[1:])
    else:
        sizes = (100, 500)
    run_benchmarks(sizes=sizes)
