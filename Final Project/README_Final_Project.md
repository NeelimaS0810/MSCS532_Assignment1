# HPC Data Structure Optimization: Cache-Friendly Memory Layouts

> **CSCI 532 – Data Structures and Algorithms | Final Project**

## Overview

This project demonstrates data structure optimization techniques identified in the empirical study *"An Empirical Study of High Performance Computing (HPC) Performance Bugs"* by Azad et al. (2023), published at the IEEE/ACM 20th International Conference on Mining Software Repositories (MSR 2023). The study analyzed **186 confirmed performance bugs** across **23 open-source HPC projects** and found that **39.3% of all HPC performance bugs** originate from inefficient algorithm and data structure choices.

This implementation focuses on three core optimization categories that account for over **70%** of all HPC performance bugs:

1. **Memory Layout Optimization (AoS vs SoA)** – Replacing Array of Structures with Structure of Arrays for cache-friendly data access
2. **Cache-Friendly Blocked Matrix Multiplication** – Tiling loop iterations so working sets fit in CPU cache
3. **Algorithmic Optimization (Linear vs Binary Search)** – Replacing O(n) lookups with O(log n) binary search, replicating the GROMACS commit a711d41 optimization

## Project Structure

```
hpc-optimization-project/
│
├── hpc_optimization.py        # Main implementation and benchmark suite (350+ lines)
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
└── (Generated after running)
    ├── chart_aos_vs_soa.png   # AoS vs SoA performance comparison
    ├── chart_matmul.png       # Matrix multiplication benchmark chart
    ├── chart_search.png       # Linear vs binary search scaling chart
    ├── chart_memory.png       # Memory usage comparison chart
    └── chart_speedup.png      # SoA speedup factor chart
```

## Requirements

- Python 3.8 or higher
- NumPy >= 1.21.0
- Matplotlib >= 3.5.0

## Installation and Setup

**1. Clone the repository:**

```bash
git clone https://github.com/[YOUR_USERNAME]/hpc-optimization-project.git
cd hpc-optimization-project
```

**2. Install dependencies:**

```bash
pip install -r requirements.txt
```

**3. Run the benchmarks:**

```bash
python hpc_optimization.py
```

This will execute all four benchmark suites, print detailed timing results to the console, and generate five performance comparison charts as PNG files in the current directory.

## Implementation Details

### Section 1: Array of Structures (AoS) vs Structure of Arrays (SoA)

The AoS implementation uses Python objects with `__slots__` to represent individual particles, each storing 8 attributes (x, y, z, vx, vy, vz, mass, charge). The SoA implementation stores each attribute in a separate contiguous NumPy `float64` array.

**Benchmarks included:**
- Particle position update (`x += vx * dt`)
- Pairwise neighbor distance computation
- Velocity statistics (mean and standard deviation)
- Memory usage comparison

**Why this matters:** In AoS layout, each cache line (64 bytes) loads a mix of fields. In SoA layout, every byte in a cache line contains useful data for the field being processed, enabling SIMD vectorization and hardware prefetching.

### Section 2: Cache-Friendly Blocked Matrix Multiplication

Three implementations are compared:

| Implementation | Description | Cache Behavior |
|---|---|---|
| **Naive** | Triple-loop, column-wise B access | O(n³/L) cache misses |
| **Blocked** | 64×64 tiles fitting L1 cache | O(n³/(L√M)) cache misses |
| **NumPy BLAS** | Hardware-optimized assembly | Theoretical hardware ceiling |

The blocked approach partitions matrices into sub-blocks that fit entirely in L1 cache (64 × 64 × 8 bytes = 32 KB), dramatically reducing cache misses.

### Section 3: Linear Search vs Binary Search

Replicates the optimization documented in GROMACS commit a711d41 (Azad et al., 2023), where linear molecule lookup was replaced with binary search:

- **Linear search:** O(n) using Python list iteration
- **Binary search:** O(log n) using NumPy `searchsorted` on contiguous arrays

### Section 4: Benchmarking Framework

All benchmarks use a consistent framework featuring:
- Warmup iterations (2 runs excluded from timing)
- Multiple timed repetitions (3–5 runs)
- Statistical reporting (mean, standard deviation, minimum)
- High-resolution timing via `time.perf_counter()`

## Key Results

| Optimization | Technique | Observed Speedup |
|---|---|---|
| Memory Layout | SoA (NumPy) vs AoS (Python objects) | **21–55×** |
| Matrix Multiply | Blocked tiling vs naive triple-loop | **1,637–2,599×** |
| Matrix Multiply | NumPy BLAS vs blocked Python | **1.9–5.2×** |
| Search Algorithm | Binary search vs linear search | **28–25,712×** |
| Memory Efficiency | SoA vs AoS memory footprint | **2.6× reduction** |

### Sample Console Output

```
======================================================================
HPC Data Structure Optimization - Benchmark Suite
======================================================================

BENCHMARK 1: AoS vs SoA - Particle Position Update
  N = 10,000 particles:
    AoS (Python objects):  Mean: 0.000765s
    SoA (NumPy arrays):    Mean: 0.000014s
    Speedup (SoA over AoS): 54.9x

BENCHMARK 3: Cache-Friendly Blocked Matrix Multiplication
  Matrix size: 256x256:
    Naive (triple loop):   Mean: 3.094726s
    Blocked (tile=64):     Mean: 0.001521s
    Blocked vs Naive speedup: 2035.3x

BENCHMARK 4: Linear Search vs Binary Search
  Array size: 1,000,000:
    Linear Search O(n):    Mean: 0.055122s
    Binary Search O(log n): Mean: 0.000002s
    Speedup: 25,712.2x
```

## Connection to Empirical Study

The optimizations implemented in this project map directly to the bug taxonomy from Azad et al. (2023):

| Bug Category | % of Bugs | This Project |
|---|---|---|
| Inefficient Algorithm/Data Structure (IAD) | 39.3% | AoS→SoA, Binary Search |
| Micro-Architecture Issues (MA) | 31.2% | Blocked Matrix Multiplication |
| Memory Management (MM) | 7.0% | SoA memory reduction |

The empirical study documented that performance bug fixes have a median patch size of only **35 lines of code**, yet yield speedups ranging from **1.2× to 200×**. This project confirms that insight — each optimization required minimal code changes but produced orders-of-magnitude performance improvements.

## References

1. Azad, M. A. K., Iqbal, N., Hassan, F., & Roy, P. (2023). An empirical study of high performance computing (HPC) performance bugs. *Proceedings of the IEEE/ACM 20th International Conference on Mining Software Repositories (MSR)*, 194–206. https://doi.org/10.1109/MSR59073.2023.00038

2. Trott, C. R., Lebrun-Grandié, D., Arndt, D., et al. (2022). Kokkos 3: Programming model extensions for the exascale era. *IEEE Transactions on Parallel and Distributed Systems, 33*(4), 805–817. https://doi.org/10.1109/TPDS.2021.3097283

3. Usman, M., Ahmad, I., & Khan, S. (2023). Data locality in high performance computing, big data, and converged systems. *Electronics, 12*(1), Article 53. https://doi.org/10.3390/electronics12010053

4. Bhattacharya, A., Dunn, B., Marchetti-Spaccamela, A., & Pagh, R. (2022). When are cache-oblivious algorithms cache adaptive? *Proceedings of the 30th Annual European Symposium on Algorithms (ESA)*, Article 16. https://doi.org/10.4230/LIPIcs.ESA.2022.16

5. Šmelko, A., Cejka, F., Krulis, M., & Kratochvil, M. (2023). Astute approach to handling memory layouts of regular data structures. In *Algorithms and Architectures for Parallel Processing (ICA3PP 2022)*, LNCS 13777, 486–505. https://doi.org/10.1007/978-3-031-22677-9_27

6. Sepanski, S., Zhao, T., Manasi, G., Basu, P., & Samatova, N. F. (2022). BrickLib: A performance portable stencil library. *Proceedings of SC'22*, Article 38. https://doi.org/10.1109/SC41404.2022.00042

7. Choe, J., Ahn, J., & Vijaykumar, T. N. (2022). HybriDS: Cache-conscious concurrent data structures for near-memory processing. *Proceedings of SPAA 2022*, 403–415. https://doi.org/10.1145/3490148.3538591

## License

This project is submitted as academic coursework for CSCI 532. All code is original.
