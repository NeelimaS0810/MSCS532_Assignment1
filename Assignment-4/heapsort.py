"""Heapsort implementation (max-heap) - returns a new sorted list.

Functions:
 - heapsort(iterable): returns a new list sorted in ascending order.
"""
from typing import List, Iterable


def _heapify(arr: List, n: int, i: int) -> None:
    largest = i
    l = 2 * i + 1
    r = 2 * i + 2

    if l < n and arr[l] > arr[largest]:
        largest = l
    if r < n and arr[r] > arr[largest]:
        largest = r
    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        _heapify(arr, n, largest)


def _build_max_heap(arr: List) -> None:
    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        _heapify(arr, n, i)


def heapsort(iterable: Iterable) -> List:
    """Return a new list containing the elements of `iterable` sorted ascending.

    This implementation builds a max-heap then repeatedly extracts the max.
    Time: O(n log n) worst/average/best. Space: O(n) for the output copy.
    """
    arr = list(iterable)
    n = len(arr)
    if n <= 1:
        return arr[:]

    _build_max_heap(arr)
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]
        _heapify(arr, i, 0)
    return arr


if __name__ == "__main__":
    import random
    data = [random.randint(0, 1000) for _ in range(20)]
    print("input:", data)
    print("heapsort:", heapsort(data))
