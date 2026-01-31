README.md
# MSCS532_Assignment1 - Insertion Sort

## Project Description
This project implements the **Insertion Sort** algorithm in Python as part of Assignment 1. 

The primary goal was to configure a Python development environment using Visual Studio Code and practice version control with GitHub.

## Algorithm Logic
Following the pseudocode from *Introduction to Algorithms* (Chapter 2), this implementation has been modified to sort in **monotonically decreasing order**.

### Key Modification:
In the standard increasing sort, we check `A[i] > key`. To achieve a decreasing order, the logic was updated to:
`while i >= 0 and A[i] < key:`

## Installation and Setup
1. **Python:** Requires Python 3.8 or higher.
3. **Running the code:**
 insertion_sort.py
 ## Reference:
Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). Introduction to Algorithms (4th ed.). Random House Publishing Services. 

##Assignment-2##
# Divide-and-Conquer Algorithm Analysis

This repository contains the implementation and performance analysis for **Merge Sort** and **Quick Sort** as part of Assignment 2 for the Algorithms and Data Structures course.

## Project Structure
- `sorting_algorithms.py`: Python implementation of Merge Sort and Quick Sort with a benchmarking suite.
## Algorithms Implemented
1. **Merge Sort**: A stable, comparison-based divide-and-conquer algorithm with a guaranteed Theta(n lg n) time complexity.
2. **Quick Sort**: An efficient, in-place divide-and-conquer algorithm with an average-case complexity of Theta(n \lg n).