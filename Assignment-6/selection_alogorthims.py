"""
Assignment 6 – Part 1: Selection Algorithms
============================================
Implements two algorithms for finding the k-th smallest element:
  1. Deterministic  – Median of Medians  (worst-case O(n))
  2. Randomized     – Randomized Quickselect (expected O(n))
"""

import random
import time
import sys

# ─────────────────────────────────────────────────────────────
# 1.  DETERMINISTIC SELECTION  –  Median of Medians
# ─────────────────────────────────────────────────────────────

def insertion_sort(arr: list) -> list:
    """Sort a small list in-place using insertion sort (O(n²) but fast for n≤5)."""
    a = arr[:]
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


def median_of_medians(arr: list, k: int) -> int:
    """
    Return the k-th smallest element (1-indexed) in arr using the
    deterministic Median-of-Medians algorithm.

    Time complexity : O(n) worst case
    Space complexity: O(n) due to recursion and sublists
    """
    if len(arr) == 0:
        raise ValueError("Cannot select from an empty array")
    if not (1 <= k <= len(arr)):
        raise IndexError(f"k={k} is out of range for array of length {len(arr)}")

    return _mom_select(arr[:], k)   # work on a copy


def _mom_select(arr: list, k: int) -> int:
    n = len(arr)

    # Base case – brute force for very small arrays
    if n <= 5:
        return insertion_sort(arr)[k - 1]

    # ── Step 1: Divide into groups of 5 ──────────────────────
    groups = [arr[i: i + 5] for i in range(0, n, 5)]

    # ── Step 2: Find median of each group ────────────────────
    medians = [insertion_sort(g)[len(g) // 2] for g in groups]

    # ── Step 3: Recursively find median of medians ───────────
    pivot = _mom_select(medians, (len(medians) + 1) // 2)

    # ── Step 4: Partition around pivot ───────────────────────
    low  = [x for x in arr if x < pivot]
    high = [x for x in arr if x > pivot]
    # Elements equal to pivot
    eq   = [x for x in arr if x == pivot]

    # ── Step 5: Recurse into the right partition ─────────────
    if k <= len(low):
        return _mom_select(low, k)
    elif k <= len(low) + len(eq):
        return pivot
    else:
        return _mom_select(high, k - len(low) - len(eq))


# ─────────────────────────────────────────────────────────────
# 2.  RANDOMIZED SELECTION  –  Randomized Quickselect
# ─────────────────────────────────────────────────────────────

def randomized_select(arr: list, k: int) -> int:
    """
    Return the k-th smallest element (1-indexed) in arr using
    Randomized Quickselect.

    Time complexity : O(n) expected  /  O(n²) worst case
    Space complexity: O(log n) expected (recursion stack)
    """
    if len(arr) == 0:
        raise ValueError("Cannot select from an empty array")
    if not (1 <= k <= len(arr)):
        raise IndexError(f"k={k} is out of range for array of length {len(arr)}")

    return _rqs_select(arr[:], 0, len(arr) - 1, k)


def _rqs_select(arr: list, left: int, right: int, k: int) -> int:
    if left == right:
        return arr[left]

    pivot_index = _random_partition(arr, left, right)
    # pivot_index is the rank of arr[pivot_index] among arr[left..right]
    rank = pivot_index - left + 1

    if k == rank:
        return arr[pivot_index]
    elif k < rank:
        return _rqs_select(arr, left, pivot_index - 1, k)
    else:
        return _rqs_select(arr, pivot_index + 1, right, k - rank)


def _random_partition(arr: list, left: int, right: int) -> int:
    """Choose a random pivot, swap to end, then partition."""
    pivot_idx = random.randint(left, right)
    arr[pivot_idx], arr[right] = arr[right], arr[pivot_idx]
    return _partition(arr, left, right)


def _partition(arr: list, left: int, right: int) -> int:
    """Lomuto partition scheme – returns final pivot position."""
    pivot = arr[right]
    i = left - 1
    for j in range(left, right):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[right] = arr[right], arr[i + 1]
    return i + 1


# ─────────────────────────────────────────────────────────────
# 3.  EMPIRICAL ANALYSIS
# ─────────────────────────────────────────────────────────────

def benchmark(func, arr: list, k: int, runs: int = 5) -> float:
    """Return average wall-clock time (seconds) over `runs` trials."""
    total = 0.0
    for _ in range(runs):
        data = arr[:]          # fresh copy each run
        t0 = time.perf_counter()
        func(data, k)
        total += time.perf_counter() - t0
    return total / runs


def run_empirical_analysis():
    """
    Compare deterministic vs randomized selection on various
    input sizes and distributions.
    """
    sizes        = [1_000, 5_000, 10_000, 50_000, 100_000]
    distributions = {
        "random"        : lambda n: [random.randint(0, n) for _ in range(n)],
        "sorted"        : lambda n: list(range(n)),
        "reverse-sorted": lambda n: list(range(n, 0, -1)),
        "duplicates"    : lambda n: [random.randint(0, n // 10) for _ in range(n)],
    }

    header = f"{'Distribution':<18} {'Size':>8}  {'MoM (s)':>12}  {'RQS (s)':>12}  {'Ratio MoM/RQS':>14}"
    print(header)
    print("─" * len(header))

    results = []
    for dist_name, gen in distributions.items():
        for n in sizes:
            arr = gen(n)
            k   = n // 2          # find the median element

            t_mom = benchmark(median_of_medians,  arr, k)
            t_rqs = benchmark(randomized_select,  arr, k)
            ratio = t_mom / t_rqs if t_rqs > 0 else float("inf")

            results.append({
                "distribution": dist_name,
                "size": n,
                "mom_time": t_mom,
                "rqs_time": t_rqs,
                "ratio": ratio,
            })
            print(f"{dist_name:<18} {n:>8}  {t_mom:>12.6f}  {t_rqs:>12.6f}  {ratio:>14.2f}x")
        print()

    return results


# ─────────────────────────────────────────────────────────────
# 4.  CORRECTNESS TESTS
# ─────────────────────────────────────────────────────────────

def run_correctness_tests():
    test_cases = [
        ([3, 1, 4, 1, 5, 9, 2, 6], 1, 1),
        ([3, 1, 4, 1, 5, 9, 2, 6], 4, 3),
        ([3, 1, 4, 1, 5, 9, 2, 6], 8, 9),
        ([7],                       1, 7),
        ([2, 2, 2, 2],              2, 2),     # all duplicates
        (list(range(100, 0, -1)),  50, 50),    # reverse sorted
    ]

    print("Correctness Tests")
    print("─" * 55)
    all_passed = True
    for arr, k, expected in test_cases:
        mom_result = median_of_medians(arr[:], k)
        rqs_result = randomized_select(arr[:], k)
        ok_mom = "✓" if mom_result == expected else "✗"
        ok_rqs = "✓" if rqs_result == expected else "✗"
        if mom_result != expected or rqs_result != expected:
            all_passed = False
        print(f"  arr={str(arr[:5])+'...' if len(arr)>5 else str(arr):<30} "
              f"k={k:<3} expected={expected:<5} "
              f"MoM={mom_result} {ok_mom}  RQS={rqs_result} {ok_rqs}")

    print()
    print("All tests passed!" if all_passed else "SOME TESTS FAILED.")
    print()


# ─────────────────────────────────────────────────────────────
# 5.  ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Increase recursion limit for large inputs
    sys.setrecursionlimit(200_000)

    print("=" * 65)
    print("  Assignment 6 – Part 1: Selection Algorithms")
    print("=" * 65)
    print()

    run_correctness_tests()

    print("Empirical Performance Analysis")
    print("─" * 65)
    run_empirical_analysis()