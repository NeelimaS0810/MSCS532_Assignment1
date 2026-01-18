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