README.md
# MSCS532_Assignment1 - Insertion Sort

## Project Description
This project implements the **Insertion Sort** algorithm in Python as part of Assignment 1. 

The primary goal was to configure a Python development environment using Visual Studio Code and practice version control with GitHub.

## Algorithm Logic
Following the pseudocode from *Introduction to Algorithms* (Chapter 2), this implementation has been modified to sort in **monotonically decreasing order**.

### Key Modification:
In the standard increasing sort, we check `A[i] > key`. To achieve a decreasing order, the logic was updated to:
`while i >= 0 and A[i] < key:`

## Installation and Setup
1. **Python:** Requires Python 3.8 or higher.
3. **Running the code:**
 insertion_sort.py
 ## Reference:
Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). Introduction to Algorithms (4th ed.). Random House Publishing Services. 

##Assignment-2##
# Divide-and-Conquer Algorithm Analysis

This repository contains the implementation and performance analysis for **Merge Sort** and **Quick Sort** as part of Assignment 2 for the Algorithms and Data Structures course.

## Project Structure
- `sorting_algorithms.py`: Python implementation of Merge Sort and Quick Sort with a benchmarking suite.
## Algorithms Implemented
1. **Merge Sort**: A stable, comparison-based divide-and-conquer algorithm with a guaranteed Theta(n lg n) time complexity.
2. **Quick Sort**: An efficient, in-place divide-and-conquer algorithm with an average-case complexity of Theta(n \lg n).

#####Assignment 3 — Randomized Quicksort and Hashing with Chaining#######

Overview

This folder contains implementations and small experiments for:
- Randomized Quicksort and Deterministic Quicksort (first-element pivot)
- A HashTable using chaining with dynamic resizing

Run the sorting benchmark (generates CSV + plots):

```bash
python Assignment-3/sorting.py
```

- Produces `results_sorting.csv` and PNG plots (`sorting_*.png`) in the same folder.
- The script runs multiple trials and writes mean and per-trial timings.

Run the hashing demo and benchmark (generates CSV + plot):

```bash
python Assignment-3/hashing.py
```

- Produces `results_hashing.csv` and `hashing_ops.png` in the same folder.

Files

- `sorting.py` — implementations of `randomized_quicksort` and `deterministic_quicksort`; also contains the benchmark and plotting code (run as a script).
- `hashing.py` — `HashTable` with chaining and dynamic resizing; includes demo, benchmark, and plotting when executed as a script.
- `report.md` — theoretical analysis, empirical discussion, and links to generated results.
- `results_sorting.csv`, `results_hashing.csv` — generated CSV results.
- `sorting_*.png`, `sorting_combined.png`, `hashing_ops.png` — plots generated from the CSVs.

# Assignment 4 — Heap Data Structures

Files added:

- `heapsort.py`: Heapsort implementation (max-heap based).
- `priority_queue.py`: `MaxHeap` priority queue with `insert`, `extract_max`, `increase_key`, and `is_empty`.
- `scheduler.py`: Simple scheduler simulation that uses the priority queue.
- `benchmarks.py`: Benchmarks comparing Heapsort, Quicksort, Mergesort, and Python `sorted()`.
- `report.md`: Assignment report with analysis and results (see below).

# Assignment 5: Quicksort Algorithm - Implementation, Analysis, and Randomization

## Overview

This project provides a comprehensive study of Quicksort with both **deterministic** and **randomized** implementations, theoretical complexity analysis, and empirical performance evaluation across different input distributions.

## Files Description

### 1. **quicksort.py**
Contains `QuickSortAnalyzer` class with:
- `quicksort_deterministic()`: First element as pivot
- `quicksort_randomized()`: Random pivot selection
- Statistics tracking (comparisons, swaps)
- Unit tests for validation

### 2. **benchmark_quicksort.py**
Benchmarks both implementations on:
- **Sizes:** 100, 500, 1000, 5000, 10000 elements
- **Distributions:** Random, sorted, reverse-sorted, nearly-sorted, duplicates
- **Outputs:** CSV/JSON results and performance graphs

### 3. **report.md**
Detailed analysis covering:
- Implementation details
- Time complexity: Best O(n log n), Average O(n log n), Worst O(n²)
- Space complexity: O(log n)
- Randomization impact on performance
- Empirical results and findings
## Key Findings

### Time Complexity

| Aspect | Deterministic | Randomized |
|--------|---------------|-----------|
| Best | O(n log n) | O(n log n) |
| Average | O(n log n) | O(n log n) |
| Worst | O(n²) | O(n²) rare |

### Performance on Sorted Arrays (10,000 elements)
- **Deterministic:** 0.862 seconds (O(n²))
- **Randomized:** 0.008 seconds (O(n log n))
- **Speedup:** 101.94x

### Key Insights

1. **Deterministic Weakness:** O(n²) on sorted/reverse-sorted inputs
2. **Randomized Advantage:** Consistent O(n log n) across all inputs
3. **Theory Match:** Empirical results align with complexity analysis
4. **Practical Use:** Use randomized for unknown inputs, Timsort for guaranteed worst-case

## Algorithm Complexity

### Deterministic Quicksort

**Best Case: O(n log n)** - Pivot divides array evenly
**Average Case: O(n log n)** - Random partitions  
**Worst Case: O(n²)** - Pivot always smallest/largest (sorted arrays)

### Randomized Quicksort

**Expected Time: O(n log n)** for any input
**Worst Case: O(n²)** with exponentially small probability

### Space Complexity: O(log n)
In-place sorting with O(log n) recursion depth (average)

## Comparison with Other Sorting Algorithms

| Algorithm | Time (Avg) | Time (Worst) | Space |
|-----------|-----------|------------|-------|
| Quicksort (Randomized) | O(n log n) | O(n²) rare | O(log n) |
| Merge Sort | O(n log n) | O(n log n) | O(n) |
| Heap Sort | O(n log n) | O(n log n) | O(1) |
| Timsort | O(n log n) | O(n log n) | O(n) |

## Design Choices

1. **Pivot Selection:** First element (deterministic), random element (randomized)
2. **Partitioning:** Two-pointer method, in-place sorting
3. **Recursion:** Recursive implementation for clarity
4. **Statistics:** Counters for comparisons and swaps for analysis

## Testing and Validation

Unit tests include:
- Random, sorted, reverse-sorted arrays
- Single elements, duplicate values
- Correctness verification against Python's `sorted()`

Benchmarking tests:
- Multiple input sizes (100-10000)
- 5 different distributions
- Performance comparison and analysis