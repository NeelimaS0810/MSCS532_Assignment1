"""
Quicksort Algorithm Implementation
This module contains both deterministic and randomized versions of the Quicksort algorithm.

Author: MSCS532 Student
Date: 2026
"""

import random
import sys
from typing import List, Tuple

# Increase recursion limit for large arrays
sys.setrecursionlimit(100000)


class QuickSortAnalyzer:
    """
    A class to implement and analyze both deterministic and randomized Quicksort algorithms.
    """
    
    def __init__(self):
        """Initialize the analyzer with counters for comparisons and swaps."""
        self.comparisons = 0
        self.swaps = 0
    
    def reset_counters(self):
        """Reset comparison and swap counters."""
        self.comparisons = 0
        self.swaps = 0
    
    # ==================== DETERMINISTIC QUICKSORT ====================
    
    def quicksort_deterministic(self, arr: List, start: int = 0, end: int = None) -> List:
        """
        Deterministic Quicksort implementation using first element as pivot.
        
        Time Complexity:
            - Best case: O(n log n) - when pivot divides array evenly
            - Average case: O(n log n) - random distribution
            - Worst case: O(n^2) - when pivot is always smallest/largest (sorted/reverse-sorted)
        
        Space Complexity: O(log n) - due to recursion stack
        
        Args:
            arr: List to be sorted
            start: Starting index of the subarray
            end: Ending index of the subarray
            
        Returns:
            The sorted list (sorted in-place, also returned for convenience)
        """
        if end is None:
            end = len(arr) - 1
        
        if start < end:
            # Partition the array and get the pivot position
            pivot_index = self._partition_deterministic(arr, start, end)
            
            # Recursively sort the left and right subarrays
            self.quicksort_deterministic(arr, start, pivot_index - 1)
            self.quicksort_deterministic(arr, pivot_index + 1, end)
        
        return arr
    
    def _partition_deterministic(self, arr: List, start: int, end: int) -> int:
        """
        Partition the array using the first element as pivot (deterministic approach).
        
        This function places the pivot in its correct sorted position and returns the pivot index.
        All elements smaller than pivot are on the left, all larger elements on the right.
        
        Args:
            arr: The array to partition
            start: Starting index
            end: Ending index
            
        Returns:
            The final position of the pivot
        """
        # Choose the first element as pivot
        pivot = arr[start]
        left = start + 1
        right = end
        
        while left <= right:
            # Find element larger than pivot from left
            while left <= right and arr[left] <= pivot:
                self.comparisons += 1
                left += 1
            
            # Find element smaller than pivot from right
            while left <= right and arr[right] > pivot:
                self.comparisons += 1
                right -= 1
            
            # Swap if pointers haven't crossed
            if left < right:
                arr[left], arr[right] = arr[right], arr[left]
                self.swaps += 1
        
        # Place pivot in its correct position
        arr[start], arr[right] = arr[right], arr[start]
        self.swaps += 1
        
        return right
    
    # ==================== RANDOMIZED QUICKSORT ====================
    
    def quicksort_randomized(self, arr: List, start: int = 0, end: int = None) -> List:
        """
        Randomized Quicksort implementation with random pivot selection.
        
        This version randomly selects a pivot, which significantly reduces the probability
        of encountering worst-case scenarios on sorted or reverse-sorted arrays.
        
        Time Complexity:
            - Best case: O(n log n) - lucky pivot choices
            - Average case: O(n log n) - with high probability over all random choices
            - Worst case: O(n^2) - theoretically possible but extremely unlikely
        
        Space Complexity: O(log n) - due to recursion stack
        
        Args:
            arr: List to be sorted
            start: Starting index of the subarray
            end: Ending index of the subarray
            
        Returns:
            The sorted list (sorted in-place, also returned for convenience)
        """
        if end is None:
            end = len(arr) - 1
        
        if start < end:
            # Partition the array with random pivot and get the pivot position
            pivot_index = self._partition_randomized(arr, start, end)
            
            # Recursively sort the left and right subarrays
            self.quicksort_randomized(arr, start, pivot_index - 1)
            self.quicksort_randomized(arr, pivot_index + 1, end)
        
        return arr
    
    def _partition_randomized(self, arr: List, start: int, end: int) -> int:
        """
        Partition the array using a randomly selected pivot.
        
        This approach prevents adversarial input patterns (like sorted arrays) from
        causing worst-case performance.
        
        Args:
            arr: The array to partition
            start: Starting index
            end: Ending index
            
        Returns:
            The final position of the pivot
        """
        # Randomly select a pivot index
        random_pivot_index = random.randint(start, end)
        
        # Swap the random pivot to the beginning
        arr[start], arr[random_pivot_index] = arr[random_pivot_index], arr[start]
        self.swaps += 1
        
        # Use deterministic partition logic with the random pivot at start
        pivot = arr[start]
        left = start + 1
        right = end
        
        while left <= right:
            # Find element larger than pivot from left
            while left <= right and arr[left] <= pivot:
                self.comparisons += 1
                left += 1
            
            # Find element smaller than pivot from right
            while left <= right and arr[right] > pivot:
                self.comparisons += 1
                right -= 1
            
            # Swap if pointers haven't crossed
            if left < right:
                arr[left], arr[right] = arr[right], arr[left]
                self.swaps += 1
        
        # Place pivot in its correct position
        arr[start], arr[right] = arr[right], arr[start]
        self.swaps += 1
        
        return right
    
    # ==================== UTILITY METHODS ====================
    
    def get_statistics(self) -> Tuple[int, int]:
        """
        Get the number of comparisons and swaps performed.
        
        Returns:
            Tuple of (comparisons, swaps)
        """
        return (self.comparisons, self.swaps)
    
    def get_comparison_count(self) -> int:
        """Get the number of element comparisons performed."""
        return self.comparisons
    
    def get_swap_count(self) -> int:
        """Get the number of swaps performed."""
        return self.swaps


def test_quicksort():
    """Basic test cases for Quicksort implementations."""
    analyzer = QuickSortAnalyzer()
    
    # Test 1: Random array
    print("Test 1: Random array")
    arr1 = [64, 34, 25, 12, 22, 11, 90]
    analyzer.reset_counters()
    result1 = analyzer.quicksort_deterministic(arr1.copy())
    print(f"  Input: {[64, 34, 25, 12, 22, 11, 90]}")
    print(f"  Output: {result1}")
    print(f"  Expected: {sorted([64, 34, 25, 12, 22, 11, 90])}")
    print(f"  Correct: {result1 == sorted([64, 34, 25, 12, 22, 11, 90])}\n")
    
    # Test 2: Already sorted array
    print("Test 2: Already sorted array (deterministic)")
    arr2 = [1, 2, 3, 4, 5, 6, 7]
    analyzer.reset_counters()
    result2 = analyzer.quicksort_deterministic(arr2.copy())
    print(f"  Input: {[1, 2, 3, 4, 5, 6, 7]}")
    print(f"  Output: {result2}")
    print(f"  Correct: {result2 == sorted([1, 2, 3, 4, 5, 6, 7])}\n")
    
    # Test 3: Reverse sorted array
    print("Test 3: Reverse sorted array (randomized)")
    arr3 = [7, 6, 5, 4, 3, 2, 1]
    analyzer.reset_counters()
    result3 = analyzer.quicksort_randomized(arr3.copy())
    print(f"  Input: {[7, 6, 5, 4, 3, 2, 1]}")
    print(f"  Output: {result3}")
    print(f"  Correct: {result3 == sorted([7, 6, 5, 4, 3, 2, 1])}\n")
    
    # Test 4: Single element
    print("Test 4: Single element")
    arr4 = [42]
    analyzer.reset_counters()
    result4 = analyzer.quicksort_deterministic(arr4.copy())
    print(f"  Input: {[42]}")
    print(f"  Output: {result4}")
    print(f"  Correct: {result4 == [42]}\n")
    
    # Test 5: Duplicates
    print("Test 5: Array with duplicates")
    arr5 = [5, 2, 8, 2, 9, 1, 5, 5]
    analyzer.reset_counters()
    result5 = analyzer.quicksort_deterministic(arr5.copy())
    print(f"  Input: {[5, 2, 8, 2, 9, 1, 5, 5]}")
    print(f"  Output: {result5}")
    print(f"  Expected: {sorted([5, 2, 8, 2, 9, 1, 5, 5])}")
    print(f"  Correct: {result5 == sorted([5, 2, 8, 2, 9, 1, 5, 5])}\n")


if __name__ == "__main__":
    test_quicksort()
