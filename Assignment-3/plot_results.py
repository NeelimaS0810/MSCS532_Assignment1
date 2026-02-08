import csv
import os
import matplotlib.pyplot as plt


def find_csv():
    candidates = [
        os.path.join(os.getcwd(), 'results_sorting.csv'),
        os.path.join(os.getcwd(), 'Assignment-3', 'results_sorting.csv'),
        os.path.join(os.path.dirname(__file__), 'results_sorting.csv')
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    raise FileNotFoundError('results_sorting.csv not found; run the benchmark first')


def read_results(path):
    rows = []
    with open(path, newline='') as f:
        reader = csv.DictReader(f)
        for r in reader:
            r['n'] = int(r['n'])
            r['rand_mean'] = float(r['rand_mean'])
            r['det_mean'] = float(r['det_mean'])
            rows.append(r)
    return rows


def plot_by_distribution(rows, out_dir=None):
    if out_dir is None:
        out_dir = os.path.dirname(find_csv())
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


def plot_combined(rows, out_dir=None):
    if out_dir is None:
        out_dir = os.path.dirname(find_csv())
    # For combined plot, average across distributions
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
    csv_path = find_csv()
    rows = read_results(csv_path)
    out_dir = os.path.dirname(csv_path)
    plot_by_distribution(rows, out_dir)
    plot_combined(rows, out_dir)
    print('Plots generated in', out_dir)
