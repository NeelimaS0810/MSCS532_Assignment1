# Assignment 6: Medians, Order Statistics & Elementary Data Structures

## Overview

This repository contains Python implementations and analysis for two topics from
*Introduction to Algorithms* (CLRS, 4th ed.), Chapters 9 and 10:

| Part | Topic | File |
|------|-------|------|
| 1 | Selection Algorithms (Median of Medians + Randomized Quickselect) | `part1/selection_algorithms.py` |
| 2 | Elementary Data Structures (Array, Matrix, Stack, Queue, LinkedList, Tree) | `part2/data_structures.py` |

---

## Repository Structure

```
assignment6/
├── README.md
├── part1/
│   └── selection_algorithms.py   # Deterministic & randomized selection
└── part2/
    └── data_structures.py        # All elementary data structure implementations
```

---

## Requirements

- Python 3.8 or later
- No external dependencies – only the Python standard library is used

---

## How to Run

### Part 1 – Selection Algorithms

```bash
python part1/selection_algorithms.py
```

This will:
1. Run **correctness tests** verifying both algorithms return the correct k-th smallest
   element across several edge cases (duplicates, single element, reverse-sorted, etc.)
2. Run an **empirical benchmark** comparing Median of Medians vs Randomized Quickselect
   on four input distributions (random, sorted, reverse-sorted, duplicates) and five
   array sizes (1 000 → 100 000 elements).

### Part 2 – Data Structures

```bash
python part2/data_structures.py
```

This will run a short demo for every data structure:
- `DynamicArray` – append, insert, delete, search
- `Matrix`       – add, multiply, transpose
- `Stack`        – push, pop, peek
- `Queue`        – enqueue, dequeue (circular array)
- `SinglyLinkedList` – prepend, append, insert_at, delete_value, search
- `RootedTree`   – BFS, DFS, height, depth

---

## Summary of Findings

### Part 1

| Algorithm | Worst-case | Expected | Notes |
|-----------|-----------|---------|-------|
| Median of Medians | O(n) | O(n) | High constant factor (~4× slower than RQS in practice) |
| Randomized Quickselect | O(n²) | O(n) | Faster in practice; bad pivot extremely unlikely |

Key empirical result: RQS is consistently **3–6× faster** than MoM across all
distributions and sizes, despite MoM having the stronger worst-case guarantee.
MoM is preferred only when an adversary can control the input.

### Part 2

| Data Structure | Access | Insert | Delete | Search |
|---------------|--------|--------|--------|--------|
| DynamicArray  | O(1)   | O(n)   | O(n)   | O(n) |
| Stack         | O(1) top | O(1) amort. | O(1) amort. | — |
| Queue (circular) | O(1) front | O(1) amort. | O(1) | — |
| Singly Linked List | O(n) | O(1) head / O(n) mid | O(1) head / O(n) mid | O(n) |

---