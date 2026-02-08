import random
import sys
import time
import csv
from statistics import mean

sys.setrecursionlimit(1000000)


def randomized_quicksort(arr):
    """Randomized quicksort returning a new sorted list.

    Pivot is chosen uniformly at random from the array slice.
    Handles empty arrays, repeated elements, and already-sorted inputs.
    """
    if len(arr) <= 1:
        return arr[:]

    pivot_idx = random.randint(0, len(arr) - 1)
    pivot = arr[pivot_idx]

    left = [x for i, x in enumerate(arr) if x < pivot or (x == pivot and i < pivot_idx)]
    right = [x for i, x in enumerate(arr) if x > pivot or (x == pivot and i > pivot_idx)]

    return randomized_quicksort(left) + [pivot] + randomized_quicksort(right)


def deterministic_quicksort(arr):
    """Deterministic quicksort using the first element as pivot.

    Returns a new sorted list; useful for comparing pivot strategies.
    """
    if len(arr) <= 1:
        return arr[:]

    pivot = arr[0]
    left = [x for x in arr[1:] if x < pivot]
    equal = [x for x in arr if x == pivot]
    right = [x for x in arr[1:] if x > pivot]

    return deterministic_quicksort(left) + equal + deterministic_quicksort(right)


__all__ = ["randomized_quicksort", "deterministic_quicksort"]


# ---- Benchmarking utilities (run only when executed as a script) ----
def generate_array(n, distribution):
    if distribution == 'random':
        return [random.randint(0, n) for _ in range(n)]
    if distribution == 'sorted':
        return list(range(n))
    if distribution == 'reversed':
        return list(range(n, 0, -1))
    if distribution == 'repeated':
        return [random.randint(0, max(1, n // 10)) for _ in range(n)]
    raise ValueError('unknown distribution')


def time_sort(fn, arr):
    start = time.perf_counter()
    fn(arr)
    end = time.perf_counter()
    return end - start


def run_bench(sizes, distributions, trials=3, out_csv='results_sorting.csv'):
    rows = []
    for n in sizes:
        for dist in distributions:
            times_r = []
            times_d = []
            for t in range(trials):
                arr = generate_array(n, dist)
                a1 = list(arr)
                a2 = list(arr)
                t_r = time_sort(randomized_quicksort, a1)
                t_d = time_sort(deterministic_quicksort, a2)
                times_r.append(t_r)
                times_d.append(t_d)
            row = {
                'n': n,
                'distribution': dist,
                'rand_mean': mean(times_r),
                'det_mean': mean(times_d),
                'rand_times': ';'.join(f"{x:.6f}" for x in times_r),
                'det_times': ';'.join(f"{x:.6f}" for x in times_d),
            }
            print(f"n={n} dist={dist} rand={row['rand_mean']:.6f}s det={row['det_mean']:.6f}s")
            rows.append(row)

    with open(out_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['n', 'distribution', 'rand_mean', 'det_mean', 'rand_times', 'det_times'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


if __name__ == '__main__':
    sizes = [1000, 2000, 5000, 10000]
    distributions = ['random', 'sorted', 'reversed', 'repeated']
    run_bench(sizes, distributions, trials=5)
    print('Benchmark complete. Results saved to results_sorting.csv')