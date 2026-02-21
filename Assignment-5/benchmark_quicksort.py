"""
Empirical Performance Analysis of Quicksort Algorithms
This script benchmarks deterministic and randomized Quicksort implementations
under different input distributions and array sizes.

Author: MSCS532 Student
Date: 2026
"""

import time
import random
import csv
import json
from typing import List, Dict, Tuple
from quicksort import QuickSortAnalyzer
import matplotlib.pyplot as plt
import numpy as np


class QuickSortBenchmark:
    """
    A class to benchmark and compare Quicksort implementations.
    """
    
    def __init__(self):
        """Initialize the benchmark suite."""
        self.analyzer = QuickSortAnalyzer()
        self.results = []
    
    # ==================== INPUT GENERATION ====================
    
    @staticmethod
    def generate_random_array(n: int, seed: int = None) -> List:
        """
        Generate a random array of size n.
        
        Args:
            n: Size of the array
            seed: Random seed for reproducibility
            
        Returns:
            List of random integers
        """
        if seed is not None:
            random.seed(seed)
        return [random.randint(1, 10000) for _ in range(n)]
    
    @staticmethod
    def generate_sorted_array(n: int) -> List:
        """
        Generate a sorted array (best case for deterministic, worst case for some).
        
        Args:
            n: Size of the array
            
        Returns:
            List of sorted integers
        """
        return list(range(1, n + 1))
    
    @staticmethod
    def generate_reverse_sorted_array(n: int) -> List:
        """
        Generate a reverse-sorted array (worst case scenario).
        
        Args:
            n: Size of the array
            
        Returns:
            List of reverse-sorted integers
        """
        return list(range(n, 0, -1))
    
    @staticmethod
    def generate_nearly_sorted_array(n: int, percent_unsorted: float = 0.1, seed: int = None) -> List:
        """
        Generate a nearly-sorted array with a percentage of elements out of order.
        
        Args:
            n: Size of the array
            percent_unsorted: Percentage of elements to shuffle (0.1 = 10%)
            seed: Random seed
            
        Returns:
            List that is mostly sorted
        """
        if seed is not None:
            random.seed(seed)
        arr = list(range(1, n + 1))
        num_to_shuffle = int(n * percent_unsorted)
        shuffle_indices = random.sample(range(n), num_to_shuffle)
        for i in shuffle_indices:
            arr[i] = random.randint(1, n)
        return arr
    
    @staticmethod
    def generate_duplicates_array(n: int, num_unique: int = 10, seed: int = None) -> List:
        """
        Generate an array with many duplicate values.
        
        Args:
            n: Size of the array
            num_unique: Number of unique values
            seed: Random seed
            
        Returns:
            List with many duplicates
        """
        if seed is not None:
            random.seed(seed)
        return [random.randint(1, num_unique) for _ in range(n)]
    
    # ==================== BENCHMARKING METHODS ====================
    
    def benchmark_implementation(self, sort_func, arr: List, name: str) -> Tuple[float, int, int]:
        """
        Benchmark a single sort implementation.
        
        Args:
            sort_func: The sorting function to benchmark
            arr: Array to sort (will be copied)
            name: Name of the implementation
            
        Returns:
            Tuple of (execution_time, comparisons, swaps)
        """
        test_arr = arr.copy()
        self.analyzer.reset_counters()
        
        start_time = time.perf_counter()
        sort_func(test_arr)
        end_time = time.perf_counter()
        
        execution_time = end_time - start_time
        comparisons, swaps = self.analyzer.get_statistics()
        
        return execution_time, comparisons, swaps
    
    def run_comprehensive_benchmark(self, sizes: List[int] = None) -> Dict:
        """
        Run comprehensive benchmarks across different array sizes and distributions.
        
        Args:
            sizes: List of array sizes to test
            
        Returns:
            Dictionary containing all benchmark results
        """
        if sizes is None:
            sizes = [100, 500, 1000, 5000, 10000]
        
        distributions = {
            'random': self.generate_random_array,
            'sorted': self.generate_sorted_array,
            'reverse_sorted': self.generate_reverse_sorted_array,
            'nearly_sorted': self.generate_nearly_sorted_array,
            'duplicates': self.generate_duplicates_array,
        }
        
        all_results = {}
        
        for dist_name, dist_func in distributions.items():
            print(f"\n{'='*60}")
            print(f"Testing distribution: {dist_name.upper()}")
            print(f"{'='*60}")
            
            all_results[dist_name] = {}
            
            for size in sizes:
                print(f"\nArray size: {size}")
                
                # Generate test array
                if dist_name == 'nearly_sorted':
                    test_arr = dist_func(size, percent_unsorted=0.1, seed=42)
                elif dist_name == 'duplicates':
                    test_arr = dist_func(size, num_unique=10, seed=42)
                elif dist_name == 'random':
                    test_arr = dist_func(size, seed=42)
                else:
                    test_arr = dist_func(size)
                
                # Benchmark deterministic quicksort
                time_det, comp_det, swap_det = self.benchmark_implementation(
                    self.analyzer.quicksort_deterministic,
                    test_arr,
                    "Deterministic"
                )
                
                # Benchmark randomized quicksort
                time_rand, comp_rand, swap_rand = self.benchmark_implementation(
                    self.analyzer.quicksort_randomized,
                    test_arr,
                    "Randomized"
                )
                
                result = {
                    'size': size,
                    'distribution': dist_name,
                    'deterministic': {
                        'time': time_det,
                        'comparisons': comp_det,
                        'swaps': swap_det
                    },
                    'randomized': {
                        'time': time_rand,
                        'comparisons': comp_rand,
                        'swaps': swap_rand
                    },
                    'speedup': time_det / time_rand if time_rand > 0 else 0
                }
                
                all_results[dist_name][size] = result
                
                # Print results
                print(f"  Deterministic: Time={time_det:.6f}s, Comparisons={comp_det}, Swaps={swap_det}")
                print(f"  Randomized:    Time={time_rand:.6f}s, Comparisons={comp_rand}, Swaps={swap_rand}")
                print(f"  Speedup: {result['speedup']:.2f}x")
        
        return all_results
    
    def save_results_to_csv(self, results: Dict, filename: str = 'quicksort_benchmarks.csv'):
        """
        Save benchmark results to a CSV file.
        
        Args:
            results: Dictionary of benchmark results
            filename: Output CSV filename
        """
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'Distribution', 'Size', 'Det_Time', 'Det_Comp', 'Det_Swaps',
                'Rand_Time', 'Rand_Comp', 'Rand_Swaps', 'Speedup'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for dist_name, size_results in results.items():
                for size, result in size_results.items():
                    writer.writerow({
                        'Distribution': dist_name,
                        'Size': size,
                        'Det_Time': result['deterministic']['time'],
                        'Det_Comp': result['deterministic']['comparisons'],
                        'Det_Swaps': result['deterministic']['swaps'],
                        'Rand_Time': result['randomized']['time'],
                        'Rand_Comp': result['randomized']['comparisons'],
                        'Rand_Swaps': result['randomized']['swaps'],
                        'Speedup': result['speedup']
                    })
        
        print(f"\nResults saved to {filename}")
    
    def save_results_to_json(self, results: Dict, filename: str = 'quicksort_benchmarks.json'):
        """
        Save benchmark results to a JSON file.
        
        Args:
            results: Dictionary of benchmark results
            filename: Output JSON filename
        """
        with open(filename, 'w') as jsonfile:
            json.dump(results, jsonfile, indent=2)
        
        print(f"Results saved to {filename}")


def plot_results(results: Dict):
    """
    Create visualizations of the benchmark results.
    
    Args:
        results: Dictionary of benchmark results
    """
    distributions = list(results.keys())
    num_dists = len(distributions)
    
    # Create figure with subplots for each distribution
    fig, axes = plt.subplots(num_dists, 1, figsize=(12, 5 * num_dists))
    if num_dists == 1:
        axes = [axes]
    
    for idx, (dist_name, size_results) in enumerate(results.items()):
        sizes = sorted(size_results.keys())
        det_times = [size_results[s]['deterministic']['time'] for s in sizes]
        rand_times = [size_results[s]['randomized']['time'] for s in sizes]
        
        ax = axes[idx]
        ax.plot(sizes, det_times, 'o-', label='Deterministic', linewidth=2, markersize=6)
        ax.plot(sizes, rand_times, 's-', label='Randomized', linewidth=2, markersize=6)
        ax.set_xlabel('Array Size', fontsize=11)
        ax.set_ylabel('Time (seconds)', fontsize=11)
        ax.set_title(f'Quicksort Performance on {dist_name.replace("_", " ").title()} Arrays', 
                     fontsize=12, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('quicksort_performance.png', dpi=300, bbox_inches='tight')
    print("\nPerformance plot saved as quicksort_performance.png")
    plt.close()


def main():
    """Run the complete benchmark suite."""
    print("=" * 70)
    print("QUICKSORT EMPIRICAL ANALYSIS".center(70))
    print("=" * 70)
    
    benchmark = QuickSortBenchmark()
    
    # Run comprehensive benchmarks
    sizes = [100, 500, 1000, 5000, 10000]
    results = benchmark.run_comprehensive_benchmark(sizes)
    
    # Save results
    benchmark.save_results_to_csv(results, 'quicksort_benchmarks.csv')
    benchmark.save_results_to_json(results, 'quicksort_benchmarks.json')
    
    # Create visualizations
    plot_results(results)
    
    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
