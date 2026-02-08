import random
import sys
import time
import csv
from statistics import mean
import os

import matplotlib.pyplot as plt

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


# ---- Plotting utilities (reads results_sorting.csv and writes PNGs) ----
def _find_csv(out_csv='results_sorting.csv'):
    candidates = [
        os.path.join(os.getcwd(), out_csv),
        os.path.join(os.path.dirname(__file__), out_csv),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), out_csv),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f'{out_csv} not found; run the benchmark first')


def _read_results(path):
    rows = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            r['n'] = int(r['n'])
            r['rand_mean'] = float(r['rand_mean'])
            r['det_mean'] = float(r['det_mean'])
            rows.append(r)
    return rows


def _plot_by_distribution(rows, out_dir=None):
    if out_dir is None:
        out_dir = os.path.dirname(_find_csv())
    dist_map = {}
    for r in rows:
        dist_map.setdefault(r['distribution'], []).append(r)

    for dist, items in dist_map.items():
        items.sort(key=lambda x: x['n'])
        ns = [i['n'] for i in items]
        rand = [i['rand_mean'] for i in items]
        det = [i['det_mean'] for i in items]

        plt.figure()
        plt.plot(ns, rand, marker='o', label='Randomized Quicksort')
        plt.plot(ns, det, marker='o', label='Deterministic Quicksort')
        plt.xlabel('n (array size)')
        plt.ylabel('Time (s)')
        plt.title(f'Quicksort performance — {dist}')
        plt.legend()
        plt.grid(True)
        out_path = os.path.join(out_dir, f'sorting_{dist}.png')
        plt.savefig(out_path)
        plt.close()
        print('Saved', out_path)


def _plot_combined(rows, out_dir=None):
    if out_dir is None:
        out_dir = os.path.dirname(_find_csv())
    dist_items = {}
    for r in rows:
        dist_items.setdefault(r['distribution'], []).append(r)

    plt.figure()
    for dist, items in dist_items.items():
        items.sort(key=lambda x: x['n'])
        ns = [i['n'] for i in items]
        rand = [i['rand_mean'] for i in items]
        det = [i['det_mean'] for i in items]
        plt.plot(ns, rand, marker='o', label=f'Rand ({dist})')
        plt.plot(ns, det, marker='x', linestyle='--', label=f'Det ({dist})')

    plt.xlabel('n (array size)')
    plt.ylabel('Time (s)')
    plt.title('Quicksort performance across distributions')
    plt.legend()
    plt.grid(True)
    out_path = os.path.join(out_dir, 'sorting_combined.png')
    plt.savefig(out_path)
    plt.close()
    print('Saved', out_path)


if __name__ == '__main__':
    sizes = [1000, 2000, 5000, 10000]
    distributions = ['random', 'sorted', 'reversed', 'repeated']
    out_csv = 'results_sorting.csv'
    run_bench(sizes, distributions, trials=5, out_csv=out_csv)
    print('Benchmark complete. Results saved to', out_csv)

    # generate plots from the produced CSV
    try:
        csv_path = _find_csv(out_csv)
        rows = _read_results(csv_path)
        out_dir = os.path.dirname(csv_path)
        _plot_by_distribution(rows, out_dir)
        _plot_combined(rows, out_dir)
        print('Plots generated in', out_dir)
    except Exception as e:
        print('Plot generation skipped:', e)