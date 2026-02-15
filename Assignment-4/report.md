# Assignment 4 — Heap Data Structures: Implementation, Analysis, and Applications
Summary
 - Implemented Heapsort (`heapsort.py`) using an array-backed max-heap.
 - Implemented a `Task` dataclass embedded in `priority_queue.py` and a `MaxHeap` priority queue (`priority_queue.py`).

Heapsort Implementation and Analysis
 - Implementation: builds a max-heap in O(n) then extracts the maximum n times, each extraction O(log n).
 - Time complexity: O(n log n) in worst, average, and best cases.
   - Building the heap: O(n).
   - Each of n extractions costs O(log n) (heapify), so O(n log n) total.
 - Space complexity: this `heapsort` returns a new list (O(n) additional); an in-place variant is possible.

Priority Queue Design
 - Data structure: array-backed binary heap (`list`), chosen for compactness and O(log n) operations.
 - Task: `Task(task_id, priority, arrival, deadline, payload)` is defined inside `priority_queue.py`.
 - Policy: max-heap (highest priority first).
 - Operations and complexities:
   - `insert(task)`: append + sift-up => O(log n) worst-case.
   - `extract_max()`: swap root with last + pop + heapify => O(log n) worst-case.
   - `increase_key(task_id, new_priority)`: linear scan to find the task O(n) then sift-up/heapify O(log n) => O(n) overall (can be improved with an index map).
   - `is_empty()`: O(1).

Usage
 - Heapsort demo: run `python heapsort.py` to see a small randomized example.
 - Priority queue demo: run `python priority_queue.py` to exercise the `MaxHeap` with sample `Task` objects.

Further improvements
 - Add an index map (task_id -> heap index) to make `increase_key` O(log n).
 - Implement a stable or min-heap variant for alternative scheduling policies.
 - Extend demos to include scheduler simulations or benchmarks as needed.

Additions and smoke-test results
 - Implemented an index map in `priority_queue.py` (`pos`) so `increase_key` is O(log n); added `decrease_key` (alias).
 - Re-added quick demos: `scheduler.py` (priority-based scheduler) and `benchmarks.py` (small-size smoke benchmarks).
 - Quick scheduler run (200 tasks, seed=42) produced: `{'served': 200, 'avg_wait': 0.1558, 'missed_deadlines': 3}`.
 - Small benchmark observations (averaged per small trials):
   - n=100 (random): heapsort ~0.00016s, quicksort ~0.00011s, mergesort ~0.00016s, Python `sorted()` ~1e-05s.
   - n=500 (random): heapsort ~0.0010s, quicksort ~0.0007s, mergesort ~0.0008s, Python `sorted()` ~5e-05s.
 - Interpretation: Heapsort performs as O(n log n) but has higher constant factors than optimized library sort; these smoke numbers are small-scale — run larger experiments with `benchmarks.py` for robust results.
