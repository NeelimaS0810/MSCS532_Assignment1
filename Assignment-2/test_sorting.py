import random
import sorting_algorithms as sa


def run_unit_tests():
    tests = [
        [],
        [1],
        [2, 1],
        [1, 2, 3],
        [3, 2, 1],
        [5, 3, 5, 2, 2, 9],
        [0, -1, 5, 3, -1]
    ]

    for t in tests:
        expected = sorted(t)
        m_time, m_sorted = sa.benchmark(sa.merge_sort, t)
        q_time, q_sorted = sa.benchmark(sa.quick_sort, t)
        assert m_sorted == expected, f"merge_sort failed for {t}"
        assert q_sorted == expected, f"quick_sort failed for {t}"

    print("All unit tests passed.")


if __name__ == '__main__':
    print("Running unit tests...")
    run_unit_tests()

    print('\nQuick benchmark (n=10,000):')
    sa.run_tests(sizes=[10000])
