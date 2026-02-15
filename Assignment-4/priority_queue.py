"""Max-heap based priority queue for Task objects.

Provides: MaxHeap with insert, extract_max, increase_key, is_empty.
"""
from dataclasses import dataclass
from typing import List, Optional, Any


@dataclass
class Task:
    task_id: int
    priority: int
    arrival: float = 0.0
    deadline: Optional[float] = None
    payload: Any = None

    def __repr__(self) -> str:
        return f"Task(id={self.task_id}, p={self.priority}, a={self.arrival}, d={self.deadline})"


class MaxHeap:
    def __init__(self):
        self.heap: List[Task] = []
        self.pos: dict[int, int] = {}  # task_id -> index in heap

    def _parent(self, i: int) -> int:
        return (i - 1) // 2

    def _left(self, i: int) -> int:
        return 2 * i + 1

    def _right(self, i: int) -> int:
        return 2 * i + 2

    def insert(self, task: Task) -> None:
        self.heap.append(task)
        idx = len(self.heap) - 1
        self.pos[task.task_id] = idx
        self._sift_up(idx)

    def _sift_up(self, i: int) -> None:
        while i > 0 and self.heap[self._parent(i)].priority < self.heap[i].priority:
            p = self._parent(i)
            self.heap[p], self.heap[i] = self.heap[i], self.heap[p]
            # update positions
            self.pos[self.heap[p].task_id] = p
            self.pos[self.heap[i].task_id] = i
            i = p

    def extract_max(self) -> Optional[Task]:
        if not self.heap:
            return None
        top = self.heap[0]
        last = self.heap.pop()
        del self.pos[top.task_id]
        if self.heap:
            self.heap[0] = last
            self.pos[last.task_id] = 0
            self._heapify(0)
        return top

    def _heapify(self, i: int) -> None:
        n = len(self.heap)
        while True:
            l = self._left(i)
            r = self._right(i)
            largest = i
            if l < n and self.heap[l].priority > self.heap[largest].priority:
                largest = l
            if r < n and self.heap[r].priority > self.heap[largest].priority:
                largest = r
            if largest == i:
                break
            self.heap[i], self.heap[largest] = self.heap[largest], self.heap[i]
            # update positions
            self.pos[self.heap[i].task_id] = i
            self.pos[self.heap[largest].task_id] = largest
            i = largest

    def increase_key(self, task_id: int, new_priority: int) -> bool:
        idx = self.pos.get(task_id)
        if idx is None:
            return False
        old = self.heap[idx].priority
        self.heap[idx].priority = new_priority
        if new_priority > old:
            self._sift_up(idx)
        else:
            self._heapify(idx)
        return True

    def decrease_key(self, task_id: int, new_priority: int) -> bool:
        return self.increase_key(task_id, new_priority)

    def is_empty(self) -> bool:
        return len(self.heap) == 0

    def peek(self) -> Optional[Task]:
        return self.heap[0] if self.heap else None


if __name__ == "__main__":
    # quick manual check
    tasks = [Task(i, priority=i % 5) for i in range(10)]
    pq = MaxHeap()
    for t in tasks:
        pq.insert(t)
    while not pq.is_empty():
        print(pq.extract_max())
