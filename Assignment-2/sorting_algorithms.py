import time
import random
import sys

# Increase recursion depth for deep Quick Sort trees on large sorted datasets
sys.setrecursionlimit(20000)

def merge_sort(arr):
    """
    Implementation of Merge Sort as described in CLRS Chapter 2.
    Time Complexity: Theta(n log n)
    Space Complexity: O(n)
    """
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def quick_sort(arr):
    """
    Implementation of Quick Sort using a middle-element pivot.
    Average Time Complexity: Theta(n log n)
    Worst Case: O(n^2)
    """
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)

def benchmark(algorithm, data):
    """Run `algorithm` on a copy of `data` and return elapsed time and result."""
    start = time.perf_counter()
    result = algorithm(data.copy())
    elapsed = time.perf_counter() - start
    return elapsed, result

def run_tests(sizes=[1000, 5000, 10000]):
    print(f"{'Size':<10} | {'Type':<15} | {'Merge Sort':<12} | {'Quick Sort':<12}")
    print("-" * 70)

    for n in sizes:
        datasets = {
            "Random": [random.randint(0, 100000) for _ in range(n)],
            "Sorted": list(range(n)),
            "Reverse": list(range(n, 0, -1))
        }

        for name, data in datasets.items():
            m_time, m_sorted = benchmark(merge_sort, data)
            q_time, q_sorted = benchmark(quick_sort, data)

            # Sanity-check correctness
            expected = sorted(data)
            if m_sorted != expected or q_sorted != expected:
                print(f"[ERROR] Sorting mismatch for n={n}, type={name}")

            print(f"{n:<10} | {name:<15} | {m_time:.5f}s     | {q_time:.5f}s")

if __name__ == "__main__":
    run_tests()