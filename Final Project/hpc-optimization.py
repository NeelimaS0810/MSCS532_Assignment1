"""
HPC Data Structure Optimization: Cache-Friendly Memory Layouts
==============================================================

This project demonstrates data structure optimization techniques identified
in the empirical study "An Empirical Study of High Performance Computing
(HPC) Performance Bugs" by Azad et al. (2023).

Focus: Memory layout optimization (Array of Structures vs Structure of Arrays)
and cache-friendly blocked matrix multiplication.

Author: [Your Name]
Course: CSCI 532 - Data Structures and Algorithms
Date: 2026
GitHub: [Your GitHub Repository URL]
"""

import numpy as np
import time
import sys
import os
from dataclasses import dataclass
from typing import List, Tuple

# ============================================================================
# SECTION 1: Array of Structures (AoS) vs Structure of Arrays (SoA)
# ============================================================================

class ParticleAoS:
    """
    Array of Structures (AoS) layout for particle simulation.
    Each particle object stores all its attributes together in memory.
    This causes cache pollution when only a subset of fields is needed.
    """
    __slots__ = ['x', 'y', 'z', 'vx', 'vy', 'vz', 'mass', 'charge']

    def __init__(self, x=0.0, y=0.0, z=0.0, vx=0.0, vy=0.0, vz=0.0,
                 mass=1.0, charge=0.0):
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.mass = mass
        self.charge = charge


class ParticleSystemSoA:
    """
    Structure of Arrays (SoA) layout for particle simulation.
    Each attribute is stored in a separate contiguous NumPy array.
    This maximizes cache utilization when processing one field at a time.
    
    Reference: Azad et al. (2023) found that 39.3% of HPC performance bugs
    stem from inefficient data structure choices, with cache-unfriendly
    layouts being a primary contributor.
    """

    def __init__(self, n: int):
        self.n = n
        self.x = np.random.randn(n).astype(np.float64)
        self.y = np.random.randn(n).astype(np.float64)
        self.z = np.random.randn(n).astype(np.float64)
        self.vx = np.zeros(n, dtype=np.float64)
        self.vy = np.zeros(n, dtype=np.float64)
        self.vz = np.zeros(n, dtype=np.float64)
        self.mass = np.ones(n, dtype=np.float64)
        self.charge = np.zeros(n, dtype=np.float64)


def create_aos_particles(n: int) -> List[ParticleAoS]:
    """Create n particles in AoS layout using Python objects."""
    particles = []
    np.random.seed(42)
    for i in range(n):
        p = ParticleAoS(
            x=np.random.randn(), y=np.random.randn(), z=np.random.randn(),
            vx=0.0, vy=0.0, vz=0.0, mass=1.0, charge=0.0
        )
        particles.append(p)
    return particles


def create_soa_particles(n: int) -> ParticleSystemSoA:
    """Create n particles in SoA layout using contiguous NumPy arrays."""
    np.random.seed(42)
    return ParticleSystemSoA(n)


# --- Benchmark: Position Update ---

def update_positions_aos(particles: List[ParticleAoS], dt: float = 0.01):
    """
    Update particle positions using AoS layout.
    Each iteration accesses x, y, z, vx, vy, vz from different memory
    locations (pointer chasing through Python objects).
    """
    for p in particles:
        p.x += p.vx * dt
        p.y += p.vy * dt
        p.z += p.vz * dt


def update_positions_soa(system: ParticleSystemSoA, dt: float = 0.01):
    """
    Update particle positions using SoA layout with NumPy vectorization.
    Contiguous memory access enables SIMD vectorization and optimal
    cache line utilization.
    
    Performance Insight: Each cache line (64 bytes) holds 8 contiguous
    float64 values. In SoA layout, processing x-coordinates fetches
    only x data. In AoS, each cache line contains mixed fields.
    """
    system.x += system.vx * dt
    system.y += system.vy * dt
    system.z += system.vz * dt


# --- Benchmark: Distance Computation ---

def compute_distances_aos(particles: List[ParticleAoS]) -> float:
    """
    Compute sum of pairwise distances (subset) using AoS layout.
    Demonstrates poor spatial locality with Python object access.
    """
    total = 0.0
    n = len(particles)
    limit = min(n, 2000)  # Limit for tractable computation
    for i in range(limit):
        for j in range(i + 1, min(i + 50, limit)):
            dx = particles[i].x - particles[j].x
            dy = particles[i].y - particles[j].y
            dz = particles[i].z - particles[j].z
            total += (dx * dx + dy * dy + dz * dz) ** 0.5
    return total


def compute_distances_soa(system: ParticleSystemSoA) -> float:
    """
    Compute sum of pairwise distances (subset) using SoA layout.
    Vectorized operations leverage contiguous memory and SIMD instructions.
    """
    n = system.n
    limit = min(n, 2000)
    total = 0.0
    x = system.x[:limit]
    y = system.y[:limit]
    z = system.z[:limit]
    for i in range(limit):
        j_end = min(i + 50, limit)
        if i + 1 >= j_end:
            continue
        dx = x[i] - x[i+1:j_end]
        dy = y[i] - y[i+1:j_end]
        dz = z[i] - z[i+1:j_end]
        total += np.sum(np.sqrt(dx*dx + dy*dy + dz*dz))
    return total


# --- Benchmark: Velocity Statistics ---

def compute_velocity_stats_aos(particles: List[ParticleAoS]) -> Tuple[float, float]:
    """Compute mean and std of velocity magnitudes using AoS layout."""
    speeds = []
    for p in particles:
        speed = (p.vx**2 + p.vy**2 + p.vz**2) ** 0.5
        speeds.append(speed)
    mean_speed = sum(speeds) / len(speeds)
    variance = sum((s - mean_speed)**2 for s in speeds) / len(speeds)
    return mean_speed, variance ** 0.5


def compute_velocity_stats_soa(system: ParticleSystemSoA) -> Tuple[float, float]:
    """Compute mean and std of velocity magnitudes using SoA layout."""
    speeds = np.sqrt(system.vx**2 + system.vy**2 + system.vz**2)
    return float(np.mean(speeds)), float(np.std(speeds))


# ============================================================================
# SECTION 2: Cache-Friendly Blocked Matrix Multiplication
# ============================================================================

def naive_matmul(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    Naive triple-loop matrix multiplication.
    Inner loop accesses B column-wise, causing cache misses on every
    element since B is stored in row-major (C) order.
    
    Time complexity: O(n^3)
    Cache behavior: O(n^3 / L) cache misses where L is cache line size
    """
    n = A.shape[0]
    C = np.zeros((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            total = 0.0
            for k in range(n):
                total += A[i, k] * B[k, j]
            C[i, j] = total
    return C


def blocked_matmul(A: np.ndarray, B: np.ndarray, block_size: int = 64) -> np.ndarray:
    """
    Cache-friendly blocked (tiled) matrix multiplication.
    
    Partitions matrices into blocks that fit in L1/L2 cache, dramatically
    reducing cache misses. This technique directly addresses the
    micro-architecture optimization category from Azad et al. (2023),
    which accounts for 31.2% of HPC performance bugs.
    
    Time complexity: O(n^3) (same as naive)
    Cache behavior: O(n^3 / (L * sqrt(M))) cache misses where M is cache size
    
    Args:
        A: First input matrix (n x n)
        B: Second input matrix (n x n)
        block_size: Tile size, should fit in L1 cache
                    (64 * 64 * 8 bytes = 32KB, fits in typical 32-48KB L1)
    """
    n = A.shape[0]
    C = np.zeros((n, n), dtype=np.float64)
    for ii in range(0, n, block_size):
        for jj in range(0, n, block_size):
            for kk in range(0, n, block_size):
                # Extract blocks (these fit in cache)
                i_end = min(ii + block_size, n)
                j_end = min(jj + block_size, n)
                k_end = min(kk + block_size, n)
                # Use NumPy for the inner block multiplication
                C[ii:i_end, jj:j_end] += (
                    A[ii:i_end, kk:k_end] @ B[kk:k_end, jj:j_end]
                )
    return C


def numpy_matmul(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    Optimized matrix multiplication using NumPy (BLAS backend).
    Represents the theoretical best-case with hardware-optimized
    BLAS libraries (OpenBLAS, MKL, or ATLAS).
    """
    return A @ B


# ============================================================================
# SECTION 3: Linear Search vs Binary Search Optimization
# ============================================================================

def linear_search(arr: List[int], target: int) -> int:
    """
    Linear search: O(n) time complexity.
    As identified by Azad et al. (2023), GROMACS commit a711d41
    replaced linear search with binary search for molecule lookup,
    reducing O(n) to O(log n).
    """
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1


def binary_search(arr: np.ndarray, target: int) -> int:
    """
    Binary search on sorted array: O(log n) time complexity.
    Uses NumPy's searchsorted for cache-friendly contiguous memory access.
    """
    idx = np.searchsorted(arr, target)
    if idx < len(arr) and arr[idx] == target:
        return int(idx)
    return -1


# ============================================================================
# SECTION 4: Benchmarking Framework
# ============================================================================

def benchmark(func, *args, warmup: int = 2, repeats: int = 5, label: str = ""):
    """
    Robust benchmarking function with warmup and statistical reporting.
    
    Args:
        func: Function to benchmark
        args: Arguments to pass to function
        warmup: Number of warmup iterations (excluded from timing)
        repeats: Number of timed iterations
        label: Description for output
    
    Returns:
        Tuple of (mean_time, std_time, min_time)
    """
    # Warmup phase
    for _ in range(warmup):
        func(*args)

    # Timed phase
    times = []
    for _ in range(repeats):
        start = time.perf_counter()
        result = func(*args)
        end = time.perf_counter()
        times.append(end - start)

    mean_t = np.mean(times)
    std_t = np.std(times)
    min_t = np.min(times)

    if label:
        print(f"  {label}:")
        print(f"    Mean: {mean_t:.6f}s | Std: {std_t:.6f}s | Min: {min_t:.6f}s")

    return mean_t, std_t, min_t


def run_all_benchmarks():
    """
    Execute all benchmarks and collect results for analysis.
    Returns a dictionary of results for chart generation.
    """
    results = {}
    print("=" * 70)
    print("HPC Data Structure Optimization - Benchmark Suite")
    print("=" * 70)
    print(f"System: Python {sys.version.split()[0]}, NumPy {np.__version__}")
    print(f"Platform: {sys.platform}")
    print()

    # ---- Benchmark 1: AoS vs SoA Position Update ----
    print("-" * 70)
    print("BENCHMARK 1: AoS vs SoA - Particle Position Update")
    print("-" * 70)
    sizes = [1000, 5000, 10000, 50000, 100000]
    aos_times = []
    soa_times = []

    for n in sizes:
        print(f"\n  N = {n:,} particles:")
        aos_particles = create_aos_particles(n)
        soa_system = create_soa_particles(n)

        t_aos, _, _ = benchmark(update_positions_aos, aos_particles,
                                 warmup=2, repeats=5,
                                 label="AoS (Python objects)")
        t_soa, _, _ = benchmark(update_positions_soa, soa_system,
                                 warmup=2, repeats=5,
                                 label="SoA (NumPy arrays)")

        speedup = t_aos / t_soa if t_soa > 0 else float('inf')
        print(f"    Speedup (SoA over AoS): {speedup:.1f}x")
        aos_times.append(t_aos)
        soa_times.append(t_soa)

    results['position_update'] = {
        'sizes': sizes, 'aos': aos_times, 'soa': soa_times
    }

    # ---- Benchmark 2: AoS vs SoA Distance Computation ----
    print("\n" + "-" * 70)
    print("BENCHMARK 2: AoS vs SoA - Pairwise Distance Computation")
    print("-" * 70)
    n = 5000
    print(f"\n  N = {n:,} particles (computing local neighbor distances):")
    aos_particles = create_aos_particles(n)
    soa_system = create_soa_particles(n)

    t_aos_dist, _, _ = benchmark(compute_distances_aos, aos_particles,
                                  warmup=1, repeats=3,
                                  label="AoS (Python loops)")
    t_soa_dist, _, _ = benchmark(compute_distances_soa, soa_system,
                                  warmup=1, repeats=3,
                                  label="SoA (Vectorized)")
    speedup = t_aos_dist / t_soa_dist if t_soa_dist > 0 else float('inf')
    print(f"    Speedup: {speedup:.1f}x")

    results['distance'] = {
        'aos': t_aos_dist, 'soa': t_soa_dist, 'speedup': speedup
    }

    # ---- Benchmark 3: Blocked Matrix Multiplication ----
    print("\n" + "-" * 70)
    print("BENCHMARK 3: Cache-Friendly Blocked Matrix Multiplication")
    print("-" * 70)
    mat_sizes = [64, 128, 256, 512]
    naive_times = []
    blocked_times = []
    numpy_times = []

    for n in mat_sizes:
        print(f"\n  Matrix size: {n}x{n}")
        np.random.seed(42)
        A = np.random.randn(n, n).astype(np.float64)
        B = np.random.randn(n, n).astype(np.float64)

        if n <= 256:
            t_naive, _, _ = benchmark(naive_matmul, A, B,
                                       warmup=1, repeats=2,
                                       label="Naive (triple loop)")
        else:
            # Skip naive for large sizes (too slow)
            t_naive = float('nan')
            print(f"  Naive (triple loop): SKIPPED (estimated > 60s)")

        t_blocked, _, _ = benchmark(blocked_matmul, A, B,
                                     warmup=1, repeats=3,
                                     label="Blocked (tile size=64)")
        t_numpy, _, _ = benchmark(numpy_matmul, A, B,
                                   warmup=2, repeats=5,
                                   label="NumPy (BLAS-optimized)")

        naive_times.append(t_naive)
        blocked_times.append(t_blocked)
        numpy_times.append(t_numpy)

        if not np.isnan(t_naive):
            print(f"    Blocked vs Naive speedup: {t_naive/t_blocked:.1f}x")
        print(f"    NumPy vs Blocked speedup: {t_blocked/t_numpy:.1f}x")

    results['matmul'] = {
        'sizes': mat_sizes, 'naive': naive_times,
        'blocked': blocked_times, 'numpy': numpy_times
    }

    # ---- Benchmark 4: Linear vs Binary Search ----
    print("\n" + "-" * 70)
    print("BENCHMARK 4: Linear Search vs Binary Search")
    print("-" * 70)
    search_sizes = [1000, 10000, 100000, 1000000]
    linear_times = []
    binary_times = []

    for n in search_sizes:
        print(f"\n  Array size: {n:,}")
        sorted_arr = np.arange(n)
        sorted_list = list(sorted_arr)
        target = n - 1  # Worst case for linear search

        t_lin, _, _ = benchmark(linear_search, sorted_list, target,
                                 warmup=2, repeats=5,
                                 label="Linear Search O(n)")
        t_bin, _, _ = benchmark(binary_search, sorted_arr, target,
                                 warmup=2, repeats=5,
                                 label="Binary Search O(log n)")

        speedup = t_lin / t_bin if t_bin > 0 else float('inf')
        print(f"    Speedup: {speedup:.1f}x")
        linear_times.append(t_lin)
        binary_times.append(t_bin)

    results['search'] = {
        'sizes': search_sizes, 'linear': linear_times, 'binary': binary_times
    }

    # ---- Memory Usage Comparison ----
    print("\n" + "-" * 70)
    print("MEMORY USAGE COMPARISON")
    print("-" * 70)
    n = 100000
    # AoS memory: each Python object ~168 bytes (with __slots__)
    aos_mem = n * 168  # Approximate
    # SoA memory: 8 arrays * n * 8 bytes per float64
    soa_mem = 8 * n * 8
    print(f"\n  N = {n:,} particles:")
    print(f"    AoS (Python objects): ~{aos_mem / (1024*1024):.1f} MB")
    print(f"    SoA (NumPy arrays):   ~{soa_mem / (1024*1024):.1f} MB")
    print(f"    Memory ratio (AoS/SoA): {aos_mem/soa_mem:.1f}x")

    results['memory'] = {
        'n': n, 'aos_mb': aos_mem / (1024*1024),
        'soa_mb': soa_mem / (1024*1024)
    }

    print("\n" + "=" * 70)
    print("BENCHMARKS COMPLETE")
    print("=" * 70)

    return results


# ============================================================================
# SECTION 5: Visualization (generates charts for the report)
# ============================================================================

def generate_charts(results: dict, output_dir: str = "."):
    """Generate performance comparison charts using matplotlib."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.ticker as ticker
    except ImportError:
        print("matplotlib not installed. Skipping chart generation.")
        return

    # Chart style
    plt.rcParams.update({
        'font.size': 11, 'axes.titlesize': 13, 'axes.labelsize': 11,
        'figure.facecolor': 'white', 'axes.grid': True,
        'grid.alpha': 0.3, 'legend.fontsize': 10
    })

    # ---- Chart 1: AoS vs SoA Position Update ----
    fig, ax = plt.subplots(figsize=(8, 5))
    data = results['position_update']
    x = np.arange(len(data['sizes']))
    width = 0.35
    bars1 = ax.bar(x - width/2, [t * 1000 for t in data['aos']],
                    width, label='AoS (Python Objects)', color='#e74c3c', alpha=0.85)
    bars2 = ax.bar(x + width/2, [t * 1000 for t in data['soa']],
                    width, label='SoA (NumPy Arrays)', color='#2ecc71', alpha=0.85)
    ax.set_xlabel('Number of Particles')
    ax.set_ylabel('Execution Time (ms)')
    ax.set_title('Figure 1: AoS vs SoA - Particle Position Update Performance')
    ax.set_xticks(x)
    ax.set_xticklabels([f'{s:,}' for s in data['sizes']])
    ax.legend()
    ax.set_yscale('log')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'chart_aos_vs_soa.png'), dpi=150)
    plt.close()
    print("  Generated: chart_aos_vs_soa.png")

    # ---- Chart 2: Matrix Multiplication Comparison ----
    fig, ax = plt.subplots(figsize=(8, 5))
    data = results['matmul']
    x = np.arange(len(data['sizes']))
    width = 0.25
    # Filter out NaN for naive
    naive_ms = [t * 1000 if not np.isnan(t) else 0 for t in data['naive']]
    blocked_ms = [t * 1000 for t in data['blocked']]
    numpy_ms = [t * 1000 for t in data['numpy']]

    ax.bar(x - width, naive_ms, width, label='Naive (Triple Loop)',
           color='#e74c3c', alpha=0.85)
    ax.bar(x, blocked_ms, width, label='Blocked (Tile=64)',
           color='#f39c12', alpha=0.85)
    ax.bar(x + width, numpy_ms, width, label='NumPy (BLAS)',
           color='#2ecc71', alpha=0.85)
    ax.set_xlabel('Matrix Size (N×N)')
    ax.set_ylabel('Execution Time (ms)')
    ax.set_title('Figure 2: Matrix Multiplication - Cache Optimization Impact')
    ax.set_xticks(x)
    ax.set_xticklabels([f'{s}×{s}' for s in data['sizes']])
    ax.legend()
    ax.set_yscale('log')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'chart_matmul.png'), dpi=150)
    plt.close()
    print("  Generated: chart_matmul.png")

    # ---- Chart 3: Linear vs Binary Search ----
    fig, ax = plt.subplots(figsize=(8, 5))
    data = results['search']
    ax.plot([f'{s:,}' for s in data['sizes']],
            [t * 1e6 for t in data['linear']],
            'o-', color='#e74c3c', linewidth=2, markersize=8,
            label='Linear Search O(n)')
    ax.plot([f'{s:,}' for s in data['sizes']],
            [t * 1e6 for t in data['binary']],
            's-', color='#2ecc71', linewidth=2, markersize=8,
            label='Binary Search O(log n)')
    ax.set_xlabel('Array Size')
    ax.set_ylabel('Execution Time (µs)')
    ax.set_title('Figure 3: Linear vs Binary Search Performance Scaling')
    ax.legend()
    ax.set_yscale('log')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'chart_search.png'), dpi=150)
    plt.close()
    print("  Generated: chart_search.png")

    # ---- Chart 4: Memory Usage ----
    fig, ax = plt.subplots(figsize=(6, 4))
    mem_data = results['memory']
    bars = ax.bar(['AoS\n(Python Objects)', 'SoA\n(NumPy Arrays)'],
                   [mem_data['aos_mb'], mem_data['soa_mb']],
                   color=['#e74c3c', '#2ecc71'], alpha=0.85, width=0.5)
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                f'{height:.1f} MB', ha='center', va='bottom', fontweight='bold')
    ax.set_ylabel('Memory Usage (MB)')
    ax.set_title(f'Figure 4: Memory Usage - {mem_data["n"]:,} Particles')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'chart_memory.png'), dpi=150)
    plt.close()
    print("  Generated: chart_memory.png")

    # ---- Chart 5: Speedup Summary ----
    fig, ax = plt.subplots(figsize=(8, 5))
    pos_data = results['position_update']
    speedups = [a / s for a, s in zip(pos_data['aos'], pos_data['soa'])]
    ax.bar([f'{s:,}' for s in pos_data['sizes']], speedups,
           color='#3498db', alpha=0.85)
    ax.set_xlabel('Number of Particles')
    ax.set_ylabel('Speedup (SoA / AoS)')
    ax.set_title('Figure 5: SoA Speedup Factor Over AoS by Problem Size')
    ax.axhline(y=1, color='red', linestyle='--', alpha=0.5, label='Baseline (1x)')
    for i, v in enumerate(speedups):
        ax.text(i, v + 0.5, f'{v:.0f}x', ha='center', fontweight='bold')
    ax.legend()
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, 'chart_speedup.png'), dpi=150)
    plt.close()
    print("  Generated: chart_speedup.png")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\nStarting HPC Data Structure Optimization Benchmarks...\n")

    # Run all benchmarks
    results = run_all_benchmarks()

    # Generate visualization charts
    print("\nGenerating performance charts...")
    output_dir = os.path.dirname(os.path.abspath(__file__))
    generate_charts(results, output_dir)

    print("\nAll benchmarks and charts completed successfully!")
    print("Charts saved to current directory.")
