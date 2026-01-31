def insertion_sort_decreasing(A):
    for j in range(1, len(A)):
        key = A[j]
        i = j - 1
        while i >= 0 and A[i] < key:
            A[i + 1] = A[i]
            i = i - 1
        A[i + 1] = key

if __name__ == "__main__":
    # Test data
test_array = [5, 2, 4, 6, 1, 3]
print("Original Array:", test_array)
 # Execute the sort [cite: 28]
insertion_sort_decreasing(test_array)  
# Verify the output 
print("Sorted Array (Decreasing):", test_array)