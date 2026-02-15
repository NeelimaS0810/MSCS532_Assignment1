"""Plot benchmark results from sorting_benchmarks.csv and save PNGs.

Usage: python plot_benchmarks.py
"""
import csv
import os
import math

try:
    import matplotlib.pyplot as plt
except Exception:
    print("matplotlib is required to generate plots. Install with: pip install matplotlib")
    raise


CSV_PATH = os.path.join(os.path.dirname(__file__), "sorting_benchmarks.csv")


def read_rows(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV not found: {path}. Run benchmarks.py first.")
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            # coerce types
            r2 = {"n": int(r["n"]), "kind": r["kind"], "trial": int(r["trial"])}
            for algo in ("heapsort", "quicksort", "mergesort", "py_sorted"):
                r2[algo] = float(r.get(algo, math.nan))
            rows.append(r2)
    return rows


def aggregate(rows):
    # structure: agg[kind][algo][n] = mean_time
    agg = {}
    for r in rows:
        kind = r["kind"]
        n = r["n"]
        agg.setdefault(kind, {})
        for algo in ("heapsort", "quicksort", "mergesort", "py_sorted"):
            agg[kind].setdefault(algo, {}).setdefault(n, []).append(r[algo])

    # compute means
    for kind in agg:
        for algo in agg[kind]:
            for n in agg[kind][algo]:
                vals = agg[kind][algo][n]
                agg[kind][algo][n] = sum(vals) / len(vals)
    return agg


def plot_agg(agg):
    out_dir = os.path.dirname(__file__)
    algos = ["heapsort", "quicksort", "mergesort", "py_sorted"]
    for kind, data in agg.items():
        plt.figure()
        for algo in algos:
            if algo not in data:
                continue
            items = sorted(data[algo].items())
            xs = [x for x, _ in items]
            ys = [y for _, y in items]
            plt.plot(xs, ys, marker="o", label=algo)
        plt.xlabel("n (input size)")
        plt.ylabel("time (seconds)")
        plt.title(f"Sorting benchmark ({kind})")
        plt.legend()
        plt.grid(True)
        out_path = os.path.join(out_dir, f"benchmarks_{kind}.png")
        plt.savefig(out_path)
        print(f"Saved {out_path}")
        plt.close()

    # combined plot
    plt.figure()
    colors = {"heapsort": "C0", "quicksort": "C1", "mergesort": "C2", "py_sorted": "C3"}
    for algo in algos:
        xs_all = []
        ys_all = []
        # merge across kinds by averaging times for same n
        n_map = {}
        for kind in agg:
            if algo not in agg[kind]:
                continue
            for n, t in agg[kind][algo].items():
                n_map.setdefault(n, []).append(t)
        for n in sorted(n_map.keys()):
            xs_all.append(n)
            ys_all.append(sum(n_map[n]) / len(n_map[n]))
        if xs_all:
            plt.plot(xs_all, ys_all, marker="o", label=algo, color=colors.get(algo))
    plt.xlabel("n (input size)")
    plt.ylabel("time (seconds)")
    plt.title("Sorting benchmark (combined)")
    plt.legend()
    plt.grid(True)
    out_path = os.path.join(out_dir, "benchmarks_combined.png")
    plt.savefig(out_path)
    print(f"Saved {out_path}")
    plt.close()


def main():
    rows = read_rows(CSV_PATH)
    agg = aggregate(rows)
    plot_agg(agg)


if __name__ == "__main__":
    main()
