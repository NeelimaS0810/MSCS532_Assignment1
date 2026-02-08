import random


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