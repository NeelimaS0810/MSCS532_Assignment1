"""
Assignment 6 – Visualizations
==============================
Generates all charts and diagrams for the submission report:

  Figure 1 – Empirical benchmark: MoM vs RQS (line chart, all distributions)
  Figure 2 – Grouped bar chart at n=100,000 (per distribution)
  Figure 3 – MoM / RQS ratio across sizes
  Figure 4 – Theoretical complexity curves: O(n), O(n log n), O(n²)
  Figure 5 – Data structure diagrams: Stack, Queue, Singly Linked List, Rooted Tree
  Figure 6 – Time-complexity comparison heatmap for all data structures

Run:
    python visualizations.py

Outputs:  fig1_benchmark_lines.png
          fig2_bar_n100k.png
          fig3_ratio.png
          fig4_complexity_curves.png
          fig5_ds_diagrams.png
          fig6_complexity_heatmap.png
          assignment6_all_figures.png   ← combined poster
"""

import random, sys, time, math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patches as FancyBboxPatch
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.gridspec import GridSpec
import numpy as np

sys.setrecursionlimit(200_000)

# ── colour palette ────────────────────────────────────────────
C_MOM   = "#b5451b"   # rust
C_RQS   = "#2d5a27"   # forest green
C_GOLD  = "#c8952a"
C_INK   = "#1a1a1a"
C_PAPER = "#f7f3ec"
C_MUTED = "#8a7d6e"
C_BLUE  = "#1f4e79"
C_TEAL  = "#1a6b72"

DIST_COLORS = {
    "random":         "#1f4e79",
    "sorted":         "#2d5a27",
    "reverse-sorted": "#b5451b",
    "duplicates":     "#8b2fc9",
}

plt.rcParams.update({
    "font.family":       "serif",
    "font.size":         11,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.facecolor":    C_PAPER,
    "figure.facecolor":  C_PAPER,
    "axes.labelcolor":   C_INK,
    "xtick.color":       C_MUTED,
    "ytick.color":       C_MUTED,
    "text.color":        C_INK,
    "grid.color":        "#d4c8b8",
    "grid.linewidth":    0.6,
})


# ══════════════════════════════════════════════════════════════
#  STEP 1 – Run benchmarks (or use cached data)
# ══════════════════════════════════════════════════════════════

# ── paste the two algorithms inline so this file is self-contained ──

def insertion_sort(arr):
    a = arr[:]
    for i in range(1, len(a)):
        key = a[i]; j = i - 1
        while j >= 0 and a[j] > key:
            a[j+1] = a[j]; j -= 1
        a[j+1] = key
    return a

def _mom_select(arr, k):
    n = len(arr)
    if n <= 5:
        return insertion_sort(arr)[k-1]
    groups  = [arr[i:i+5] for i in range(0, n, 5)]
    medians = [insertion_sort(g)[len(g)//2] for g in groups]
    pivot   = _mom_select(medians, (len(medians)+1)//2)
    low  = [x for x in arr if x < pivot]
    high = [x for x in arr if x > pivot]
    eq   = [x for x in arr if x == pivot]
    if   k <= len(low):              return _mom_select(low, k)
    elif k <= len(low)+len(eq):      return pivot
    else:                            return _mom_select(high, k-len(low)-len(eq))

def median_of_medians(arr, k):
    return _mom_select(arr[:], k)

def _partition(arr, l, r):
    pivot = arr[r]; i = l-1
    for j in range(l, r):
        if arr[j] <= pivot: i += 1; arr[i], arr[j] = arr[j], arr[i]
    arr[i+1], arr[r] = arr[r], arr[i+1]
    return i+1

def _rqs(arr, l, r, k):
    if l == r: return arr[l]
    pi = random.randint(l, r); arr[pi], arr[r] = arr[r], arr[pi]
    pi  = _partition(arr, l, r)
    rk  = pi - l + 1
    if   k == rk: return arr[pi]
    elif k <  rk: return _rqs(arr, l, pi-1, k)
    else:         return _rqs(arr, pi+1, r, k-rk)

def randomized_select(arr, k):
    return _rqs(arr[:], 0, len(arr)-1, k)

def benchmark(func, arr, k, runs=3):
    total = 0.0
    for _ in range(runs):
        d = arr[:]
        t0 = time.perf_counter()
        func(d, k)
        total += time.perf_counter() - t0
    return total / runs


print("Running benchmarks (this takes ~60 s) …")

SIZES = [1_000, 5_000, 10_000, 50_000, 100_000]
DISTRIBUTIONS = {
    "random":         lambda n: [random.randint(0, n) for _ in range(n)],
    "sorted":         lambda n: list(range(n)),
    "reverse-sorted": lambda n: list(range(n, 0, -1)),
    "duplicates":     lambda n: [random.randint(0, n//10) for _ in range(n)],
}

results = {}   # results[dist][size] = (mom_time, rqs_time)
for dname, gen in DISTRIBUTIONS.items():
    results[dname] = {}
    for n in SIZES:
        arr = gen(n)
        k   = n // 2
        t_mom = benchmark(median_of_medians, arr, k)
        t_rqs = benchmark(randomized_select, arr, k)
        results[dname][n] = (t_mom * 1000, t_rqs * 1000)   # → ms
        print(f"  {dname:<18} n={n:>7}  MoM={t_mom*1000:6.1f} ms  RQS={t_rqs*1000:6.1f} ms")

print("Benchmarks complete.\n")

os.makedirs("figures", exist_ok=True)


# ══════════════════════════════════════════════════════════════
#  FIGURE 1 – Line chart: all distributions × both algorithms
# ══════════════════════════════════════════════════════════════

fig1, axes = plt.subplots(2, 2, figsize=(13, 9), sharex=True)
fig1.suptitle("Figure 1 — Empirical Runtime: MoM vs Randomized Quickselect",
              fontsize=14, fontweight="bold", y=1.01)

for ax, (dname, color) in zip(axes.flat, DISTRIBUTIONS.items()):
    mom_times = [results[dname][n][0] for n in SIZES]
    rqs_times = [results[dname][n][1] for n in SIZES]

    ax.plot(SIZES, mom_times, "o-",  color=C_MOM, lw=2.2, ms=6, label="Median of Medians")
    ax.plot(SIZES, rqs_times, "s--", color=C_RQS, lw=2.2, ms=6, label="Randomized Quickselect")

    ax.fill_between(SIZES, mom_times, rqs_times, alpha=0.08, color=C_MOM)

    ax.set_title(f"Distribution: {dname}", fontsize=11, fontweight="bold")
    ax.set_ylabel("Time (ms)")
    ax.set_xlabel("Input size n")
    ax.yaxis.grid(True, linestyle="--")
    ax.xaxis.set_tick_params(rotation=20)
    ax.set_xticks(SIZES)
    ax.set_xticklabels([f"{n//1000}k" for n in SIZES])
    ax.legend(fontsize=9, framealpha=0.7)

fig1.tight_layout()
fig1.savefig("figures/fig1_benchmark_lines.png", dpi=150, bbox_inches="tight")
print("Saved fig1_benchmark_lines.png")


# ══════════════════════════════════════════════════════════════
#  FIGURE 2 – Grouped bar chart at n = 100,000
# ══════════════════════════════════════════════════════════════

fig2, ax = plt.subplots(figsize=(10, 5.5))
fig2.suptitle("Figure 2 — Runtime at n = 100,000 by Distribution",
              fontsize=14, fontweight="bold")

dists  = list(DISTRIBUTIONS.keys())
x      = np.arange(len(dists))
width  = 0.35

mom_vals = [results[d][100_000][0] for d in dists]
rqs_vals = [results[d][100_000][1] for d in dists]

bars1 = ax.bar(x - width/2, mom_vals, width, color=C_MOM, label="Median of Medians",
               zorder=3, edgecolor="white", linewidth=0.5)
bars2 = ax.bar(x + width/2, rqs_vals, width, color=C_RQS, label="Randomized Quickselect",
               zorder=3, edgecolor="white", linewidth=0.5)

for bar in (*bars1, *bars2):
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 1,
            f"{h:.1f}", ha="center", va="bottom", fontsize=8.5, color=C_MUTED)

ax.set_xticks(x)
ax.set_xticklabels(dists, fontsize=10)
ax.set_ylabel("Time (ms)")
ax.yaxis.grid(True, linestyle="--", zorder=0)
ax.legend(fontsize=10)
ax.set_ylim(0, max(mom_vals) * 1.25)

fig2.tight_layout()
fig2.savefig("figures/fig2_bar_n100k.png", dpi=150, bbox_inches="tight")
print("Saved fig2_bar_n100k.png")


# ══════════════════════════════════════════════════════════════
#  FIGURE 3 – MoM / RQS ratio across sizes
# ══════════════════════════════════════════════════════════════

fig3, ax = plt.subplots(figsize=(10, 5))
fig3.suptitle("Figure 3 — Speed Ratio: MoM / Randomized Quickselect\n(higher = MoM is slower)",
              fontsize=13, fontweight="bold")

for dname, color in DISTRIBUTIONS.items():
    ratios = [results[dname][n][0] / results[dname][n][1] for n in SIZES]
    ax.plot(SIZES, ratios, "o-", color=DIST_COLORS[dname], lw=2, ms=6, label=dname)

ax.axhline(1.0, color=C_INK, lw=1, linestyle="--", alpha=0.4, label="parity (ratio = 1)")
ax.fill_between(SIZES, 1, 8, alpha=0.04, color=C_MOM)
ax.set_xticks(SIZES)
ax.set_xticklabels([f"{n//1000}k" for n in SIZES])
ax.set_ylabel("Ratio (MoM time / RQS time)")
ax.set_xlabel("Input size n")
ax.yaxis.grid(True, linestyle="--")
ax.legend(fontsize=9, framealpha=0.8)
ax.set_ylim(0, ax.get_ylim()[1] * 1.1)

fig3.tight_layout()
fig3.savefig("figures/fig3_ratio.png", dpi=150, bbox_inches="tight")
print("Saved fig3_ratio.png")


# ══════════════════════════════════════════════════════════════
#  FIGURE 4 – Theoretical complexity curves
# ══════════════════════════════════════════════════════════════

fig4, ax = plt.subplots(figsize=(10, 5.5))
fig4.suptitle("Figure 4 — Theoretical Complexity Growth Curves",
              fontsize=14, fontweight="bold")

ns = np.linspace(1, 100_000, 500)
curves = {
    r"$O(n)$ — linear (MoM & RQS expected)":      ns,
    r"$O(n \log n)$ — comparison sort baseline":   ns * np.log2(ns),
    r"$O(n^2)$ — RQS worst case":                  ns**2 / 1000,   # scaled for visibility
}
colors = [C_RQS, C_GOLD, C_MOM]
styles = ["-", "--", ":"]

for (label, y), color, ls in zip(curves.items(), colors, styles):
    ax.plot(ns, y, color=color, lw=2.5, linestyle=ls, label=label)

ax.set_xlabel("Input size n")
ax.set_ylabel("Relative operations (arbitrary units)")
ax.set_ylim(0, ns[-1] * 1.1)
ax.set_xlim(0, 100_000)
ax.yaxis.grid(True, linestyle="--")
ax.legend(fontsize=10, framealpha=0.85)

ax.annotate("Both algorithms achieve\nO(n) in practice", xy=(80_000, 80_000),
            xytext=(50_000, 55_000),
            arrowprops=dict(arrowstyle="->", color=C_RQS),
            fontsize=9, color=C_RQS)

fig4.tight_layout()
fig4.savefig("figures/fig4_complexity_curves.png", dpi=150, bbox_inches="tight")
print("Saved fig4_complexity_curves.png")


# ══════════════════════════════════════════════════════════════
#  FIGURE 5 – Data structure diagrams
# ══════════════════════════════════════════════════════════════

def node_box(ax, x, y, text, color="#f7f3ec", border="#1a1a1a", fontsize=10, width=1.0, height=0.55):
    box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                         boxstyle="round,pad=0.05",
                         facecolor=color, edgecolor=border, linewidth=1.5, zorder=3)
    ax.add_patch(box)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            fontweight="bold", color=border, zorder=4)

def arrow(ax, x1, y1, x2, y2, color="#1a1a1a"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5), zorder=2)

fig5, axes5 = plt.subplots(1, 3, figsize=(15, 6))
fig5.suptitle("Figure 5 — Elementary Data Structure Diagrams",
              fontsize=14, fontweight="bold")
fig5.patch.set_facecolor(C_PAPER)

# ── 5a: Stack ─────────────────────────────────────────────────
ax = axes5[0]
ax.set_xlim(0, 3); ax.set_ylim(-0.5, 5.5)
ax.axis("off"); ax.set_title("Stack (LIFO)", fontweight="bold", fontsize=12)
stack_vals = ["10", "20", "30", "40"]
colors_s   = [C_PAPER, C_PAPER, C_PAPER, "#d4edd4"]
for i, (v, c) in enumerate(zip(stack_vals, colors_s)):
    node_box(ax, 1.5, i * 1.0 + 0.3, v, color=c, width=1.4)
# labels
ax.text(1.5, len(stack_vals)*1.0 + 0.55, "← TOP  (push / pop here)",
        ha="center", fontsize=8.5, color=C_MOM, style="italic")
ax.text(1.5, -0.3, "BOTTOM", ha="center", fontsize=8.5, color=C_MUTED, style="italic")
ax.annotate("", xy=(2.4, 3.4), xytext=(2.4, 2.8),
            arrowprops=dict(arrowstyle="-|>", color=C_MOM, lw=2))
ax.text(2.6, 3.1, "push", fontsize=9, color=C_MOM, fontweight="bold")

# ── 5b: Singly Linked List ────────────────────────────────────
ax = axes5[1]
ax.set_xlim(-0.3, 5.8); ax.set_ylim(-0.5, 1.5)
ax.axis("off"); ax.set_title("Singly Linked List", fontweight="bold", fontsize=12)

ll_vals = ["head", "A", "B", "C", "D", "None"]
colors_l = [C_GOLD+"88", C_PAPER, C_PAPER, C_PAPER, C_PAPER, "#e8e0d4"]
xs = [0, 1.1, 2.2, 3.3, 4.4, 5.4]

for i, (v, c, x) in enumerate(zip(ll_vals, colors_l, xs)):
    w = 0.85 if v not in ("head", "None") else 0.9
    node_box(ax, x, 0.5, v, color=c, width=w, fontsize=9)
    if i < len(ll_vals) - 1:
        arrow(ax, x + w/2, 0.5, xs[i+1] - 0.45, 0.5)

ax.text(0, -0.1, "pointer", ha="center", fontsize=7.5, color=C_MUTED)
ax.text(5.4, -0.1, "NULL", ha="center", fontsize=7.5, color=C_MUTED)

# label tail
ax.annotate("tail", xy=(4.4, 0.78), xytext=(4.4, 1.25),
            arrowprops=dict(arrowstyle="->", color=C_TEAL, lw=1.5),
            fontsize=9, color=C_TEAL, ha="center")

# ── 5c: Rooted Tree ───────────────────────────────────────────
ax = axes5[2]
ax.set_xlim(-0.5, 5.5); ax.set_ylim(-0.5, 3.5)
ax.axis("off"); ax.set_title("Rooted Tree", fontweight="bold", fontsize=12)

tree_nodes = {
    "1": (2.5, 3.0),
    "2": (1.2, 2.0), "3": (3.8, 2.0),
    "4": (0.4, 1.0), "5": (2.0, 1.0), "6": (3.2, 1.0), "7": (4.6, 1.0),
}
tree_edges = [("1","2"),("1","3"),("2","4"),("2","5"),("3","6"),("3","7")]

for (p, c) in tree_edges:
    px, py = tree_nodes[p]; cx, cy = tree_nodes[c]
    arrow(ax, px, py-0.28, cx, cy+0.28, color=C_MUTED)

for label, (x, y) in tree_nodes.items():
    depth = 0 if label=="1" else (1 if label in "23" else 2)
    color = [C_GOLD+"cc", "#d4edd4", C_PAPER][depth]
    node_box(ax, x, y, label, color=color, width=0.65, height=0.52, fontsize=10)

ax.text(2.5, 3.45, "root", ha="center", fontsize=8.5, color=C_GOLD, style="italic")
ax.text(-0.2, 0.25, "leaves", fontsize=8.5, color=C_MUTED, style="italic")

fig5.tight_layout()
fig5.savefig("figures/fig5_ds_diagrams.png", dpi=150, bbox_inches="tight")
print("Saved fig5_ds_diagrams.png")


# ══════════════════════════════════════════════════════════════
#  FIGURE 6 – Complexity heatmap
# ══════════════════════════════════════════════════════════════

fig6, ax = plt.subplots(figsize=(12, 5))
fig6.suptitle("Figure 6 — Time Complexity Summary: All Data Structures",
              fontsize=14, fontweight="bold")

structures = ["Dynamic Array", "Stack\n(array)", "Queue\n(circular)", "Singly\nLinked List", "Rooted Tree"]
operations = ["Access", "Insert\n(head)", "Insert\n(tail)", "Insert\n(mid)", "Delete\n(head)", "Delete\n(mid)", "Search"]

# encode: 0=O(1), 1=O(log n), 2=O(n), 3=O(n²)
# value, display label
data = [
    # Dynamic Array
    [(0,"O(1)"),  (2,"O(n)"),  (0,"O(1)*"), (2,"O(n)"),  (2,"O(n)"),  (2,"O(n)"),  (2,"O(n)")],
    # Stack
    [(0,"O(1)"),  (0,"—"),     (0,"O(1)*"), (0,"—"),     (0,"O(1)*"), (0,"—"),     (0,"—")],
    # Queue
    [(0,"O(1)"),  (0,"—"),     (0,"O(1)*"), (0,"—"),     (0,"O(1)"),  (0,"—"),     (0,"—")],
    # Singly Linked List
    [(2,"O(n)"),  (0,"O(1)"),  (0,"O(1)"), (2,"O(n)"),  (0,"O(1)"),  (2,"O(n)"),  (2,"O(n)")],
    # Rooted Tree
    [(2,"O(n)"),  (0,"O(1)"),  (0,"O(1)"), (0,"O(1)"),  (0,"O(1)"),  (2,"O(n)"),  (2,"O(n)")],
]

val_matrix  = np.array([[cell[0] for cell in row] for row in data], dtype=float)
label_matrix = [[cell[1] for cell in row] for row in data]

cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
    "complexity", [C_RQS, C_GOLD, C_MOM, "#6b0000"], N=256
)

im = ax.imshow(val_matrix, aspect="auto", cmap=cmap, vmin=0, vmax=3)

ax.set_xticks(range(len(operations))); ax.set_xticklabels(operations, fontsize=9)
ax.set_yticks(range(len(structures))); ax.set_yticklabels(structures, fontsize=10, fontweight="bold")
ax.tick_params(left=False, bottom=False)

for i in range(len(structures)):
    for j in range(len(operations)):
        lbl = label_matrix[i][j]
        val = val_matrix[i][j]
        fc  = "white" if val >= 1.5 else C_INK
        ax.text(j, i, lbl, ha="center", va="center", fontsize=9,
                fontweight="bold", color=fc)

# legend
legend_items = [
    mpatches.Patch(facecolor=cmap(0.0),  label="O(1)       best"),
    mpatches.Patch(facecolor=cmap(0.33), label="O(log n)"),
    mpatches.Patch(facecolor=cmap(0.67), label="O(n)"),
    mpatches.Patch(facecolor=cmap(1.0),  label="O(n²)   worst"),
]
ax.legend(handles=legend_items, loc="upper right", bbox_to_anchor=(1.18, 1.0),
          fontsize=9, framealpha=0.9, title="Complexity", title_fontsize=9)

ax.set_title("* = amortised", fontsize=8.5, loc="right", color=C_MUTED, style="italic", pad=4)

fig6.tight_layout()
fig6.savefig("figures/fig6_complexity_heatmap.png", dpi=150, bbox_inches="tight")
print("Saved fig6_complexity_heatmap.png")


# ══════════════════════════════════════════════════════════════
#  COMBINED POSTER – all 6 figures on one page
# ══════════════════════════════════════════════════════════════

from PIL import Image

img_paths = [
    "figures/fig1_benchmark_lines.png",
    "figures/fig2_bar_n100k.png",
    "figures/fig3_ratio.png",
    "figures/fig4_complexity_curves.png",
    "figures/fig5_ds_diagrams.png",
    "figures/fig6_complexity_heatmap.png",
]

imgs  = [Image.open(p) for p in img_paths]
W     = max(i.width  for i in imgs)
H_tot = sum(i.height for i in imgs)

poster = Image.new("RGB", (W, H_tot), (247, 243, 236))
y_off  = 0
for img in imgs:
    # Centre narrower images
    x_off = (W - img.width) // 2
    poster.paste(img, (x_off, y_off))
    y_off += img.height

poster.save("figures/assignment6_all_figures.png")
print("\nSaved figures/assignment6_all_figures.png  (combined poster)")
print("\n✓ All figures generated successfully in ./figures/")