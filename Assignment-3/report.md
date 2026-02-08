# Assignment 3 Report

## Part 1: Randomized Quicksort

### Implementation

- `randomized_quicksort(arr)` chooses a pivot uniformly at random from the current subarray and returns a new sorted list.
- `deterministic_quicksort(arr)` uses the first element as pivot (deterministic strategy).

### Average-case analysis

Using classic analysis via indicator random variables for comparisons: let X_{i,j}
be the indicator that elements with ranks i and j are compared during the quicksort process. For randomized quicksort, these two elements are compared iff the first pivot chosen from the subarray spanning them is either i or j. That probability is $2/(j-i+1)$.

The expected number of comparisons is:

$$
E\left[\sum_{i<j} X_{i,j}\right] = \sum_{i<j} P(X_{i,j}=1) = \sum_{i<j} \frac{2}{j-i+1} = O(n \log n).
$$

A more intuitive recurrence for expected time $T(n)$ is:

$$
T(n) = \frac{1}{n} \sum_{k=1}^n (T(k-1) + T(n-k)) + O(n),
$$

which solves to $T(n)=O(n\log n)$. The $O(n)$ term accounts for the linear partitioning work at each level, and the expected recursion depth is $O(\log n)$.

### Edge cases

Both implementations handle empty arrays, repeated elements, and already sorted inputs. Deterministic quicksort with a bad pivot (e.g., first element on sorted input) can degrade to $O(n^2)$ in practice; randomized pivoting avoids this with high probability.

### Empirical comparison

- The provided `benchmark_sorting.py` measures running times across input sizes and distributions: random, sorted, reversed, and repeated elements.
- Observed results typically show randomized quicksort performing consistently near $O(n\log n)$ across distributions, while deterministic (first-element pivot) can be significantly slower on sorted or reverse-sorted inputs.
- Small discrepancies between theory and experiment can come from recursion/overhead, Python list allocations (these implementations allocate new lists for recursion), and CPU/memory effects.

## Part 2: Hashing with Chaining

### Implementation

- `HashTable` uses chaining (Python lists) for buckets.
- Hash function: a universal-style mapping built from Python's `hash(key)` value:

$$
h(k) = ((a\cdot H(k) + b) \bmod p) \bmod m
$$

where $H(k)=\text{hash}(k)$ mapped to a non-negative integer, $p$ is a large prime, and $a,b$ are random.

- The table dynamically resizes: it grows when load factor exceeds $0.75$ and shrinks when it drops below $0.2$, rehashing entries after resizing.

### Expected times and load factor

Under simple uniform hashing, the expected cost of `search`, `insert`, and `delete` is $O(1 + \alpha)$ where $\alpha = n/m$ is the load factor. Keeping $\alpha$ bounded (e.g., by resizing) makes these operations expected $O(1)$.

Maintaining a low load factor reduces expected bucket length, minimizing traversal cost. Strategies include dynamic resizing (rehash when exceeding thresholds) and choosing a good hash function.

## Files in this folder

- `sorting.py` — randomized and deterministic quicksort implementations; also contains the benchmark code (run as a script).
- `hashing.py` — `HashTable` with chaining and dynamic resizing; includes a demo that runs when executed as a script.

Note: `benchmark_sorting.py` and `demo_hashing.py` were merged into the respective implementation files to keep the repository simple and avoid duplicate scripts.

## Running experiments

Run the sorting benchmark (produces `results_sorting.csv` in this folder):

```bash
python Assignment-3/sorting.py
```

Run the hashing demo:

```bash
python Assignment-3/hashing.py
```

Re-run the benchmarks locally to collect updated timing data; include `results_sorting.csv` in your repo when submitting.

## Submission checklist

- Ensure the repository contains:
	- `Assignment-3/sorting.py`, `Assignment-3/hashing.py`, and `Assignment-3/report.md`.
	- `results_sorting.csv` if you ran the benchmark and want to submit empirical outputs.
- Add a brief `README.md` at the repo root or inside `Assignment-3` with the run commands above.
- Push to GitHub and submit the repository URL.
