import random
import time
import csv
import os

import matplotlib.pyplot as plt


class HashTable:
    """Hash table with chaining and dynamic resizing.

    Uses a simple universal-style map from Python's `hash()` value to a slot:
    h(k) = (a * H(k) + b) mod p mod m
    where p is a large prime, and a in [1,p-1], b in [0,p-1].
    """

    def __init__(self, size=11, max_load=0.75, min_load=0.2):
        self._init_size = max(3, int(size))
        self.size = self._init_size
        self.table = [[] for _ in range(self.size)]
        self.count = 0
        self.max_load = max_load
        self.min_load = min_load

        # large prime for universal hashing; use a 61-bit Mersenne-like prime
        self._p = (1 << 61) - 1
        self._new_hash_params()

    def _new_hash_params(self):
        self._a = random.randrange(1, self._p)
        self._b = random.randrange(0, self._p)

    def _hash(self, key):
        H = hash(key)
        if H < 0:
            H = -H
        return ((self._a * H + self._b) % self._p) % self.size

    def __len__(self):
        return self.count

    def insert(self, key, value):
        idx = self._hash(key)
        bucket = self.table[idx]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i][1] = value
                return
        bucket.append([key, value])
        self.count += 1
        if self.load_factor() > self.max_load:
            self._resize(self.size * 2)

    def search(self, key):
        idx = self._hash(key)
        for k, v in self.table[idx]:
            if k == key:
                return v
        return None

    def delete(self, key):
        idx = self._hash(key)
        bucket = self.table[idx]
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self.count -= 1
                if self.size > self._init_size and self.load_factor() < self.min_load:
                    new_size = max(self._init_size, self.size // 2)
                    self._resize(new_size)
                return True
        return False

    def load_factor(self):
        return self.count / float(self.size)

    def _resize(self, new_size):
        old_items = []
        for bucket in self.table:
            for k, v in bucket:
                old_items.append((k, v))

        self.size = max(self._init_size, int(new_size))
        self.table = [[] for _ in range(self.size)]
        # change hash params to reduce clustering after resize
        self._new_hash_params()
        self.count = 0
        for k, v in old_items:
            self.insert(k, v)


def _demo(n=2000):
    import time
    ht = HashTable(size=5)
    start = time.perf_counter()
    for i in range(n):
        ht.insert(f'key{i}', i)
    t_ins = time.perf_counter() - start

    start = time.perf_counter()
    found = all(ht.search(f'key{i}') == i for i in range(n))
    t_search = time.perf_counter() - start

    start = time.perf_counter()
    for i in range(0, n, 10):
        ht.delete(f'key{i}')
    t_del = time.perf_counter() - start

    print(f'inserts={n} time={t_ins:.6f}s size={ht.size} count={len(ht)}')
    print(f'search_all time={t_search:.6f}s all_found={found}')
    print(f'deletes (every 10th) time={t_del:.6f}s size={ht.size} count={len(ht)}')


if __name__ == "__main__":
    _demo()

    def run_hash_bench(sizes=(1000, 2000, 5000, 10000), trials=5, out_csv='results_hashing.csv'):
        rows = []
        for n in sizes:
            ins_times = []
            search_times = []
            del_times = []
            for t in range(trials):
                ht = HashTable(size=5)
                # inserts
                start = time.perf_counter()
                for i in range(n):
                    ht.insert(f'key{i}', i)
                ins_times.append(time.perf_counter() - start)

                # searches
                start = time.perf_counter()
                _ = all(ht.search(f'key{i}') == i for i in range(n))
                search_times.append(time.perf_counter() - start)

                # deletes every 10th
                start = time.perf_counter()
                for i in range(0, n, 10):
                    ht.delete(f'key{i}')
                del_times.append(time.perf_counter() - start)

            row = {
                'n': n,
                'ins_mean': sum(ins_times) / len(ins_times),
                'search_mean': sum(search_times) / len(search_times),
                'del_mean': sum(del_times) / len(del_times),
                'ins_times': ';'.join(f"{x:.6f}" for x in ins_times),
                'search_times': ';'.join(f"{x:.6f}" for x in search_times),
                'del_times': ';'.join(f"{x:.6f}" for x in del_times),
            }
            print(f"n={n} ins={row['ins_mean']:.6f}s search={row['search_mean']:.6f}s del={row['del_mean']:.6f}s")
            rows.append(row)

        with open(out_csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['n', 'ins_mean', 'search_mean', 'del_mean', 'ins_times', 'search_times', 'del_times'])
            writer.writeheader()
            for r in rows:
                writer.writerow(r)

        return out_csv

    def _find_csv(out_csv='results_hashing.csv'):
        candidates = [
            os.path.join(os.getcwd(), out_csv),
            os.path.join(os.path.dirname(__file__), out_csv),
        ]
        for p in candidates:
            if os.path.exists(p):
                return p
        raise FileNotFoundError(f'{out_csv} not found')

    def _read_hash_results(path):
        rows = []
        with open(path, newline='') as f:
            reader = csv.DictReader(f)
            for r in reader:
                r['n'] = int(r['n'])
                r['ins_mean'] = float(r['ins_mean'])
                r['search_mean'] = float(r['search_mean'])
                r['del_mean'] = float(r['del_mean'])
                rows.append(r)
        return rows

    def _plot_hash_results(rows, out_dir=None):
        if out_dir is None:
            out_dir = os.path.dirname(_find_csv())
        rows.sort(key=lambda x: x['n'])
        ns = [r['n'] for r in rows]
        ins = [r['ins_mean'] for r in rows]
        search = [r['search_mean'] for r in rows]
        dels = [r['del_mean'] for r in rows]

        plt.figure()
        plt.plot(ns, ins, marker='o', label='Insert (mean)')
        plt.plot(ns, search, marker='o', label='Search (mean)')
        plt.plot(ns, dels, marker='o', label='Delete (mean)')
        plt.xlabel('n (number of keys)')
        plt.ylabel('Time (s)')
        plt.title('HashTable operation times')
        plt.legend()
        plt.grid(True)
        out_path = os.path.join(out_dir, 'hashing_ops.png')
        plt.savefig(out_path)
        plt.close()
        print('Saved', out_path)

    # run benchmark and plotting
    try:
        csv_path = run_hash_bench()
        rows = _read_hash_results(csv_path)
        _plot_hash_results(rows)
    except Exception as e:
        print('Hash benchmark/plotting skipped:', e)