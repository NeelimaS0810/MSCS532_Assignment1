"""Scheduler simulation using the MaxHeap priority queue.

Usage: `python scheduler.py [num_tasks] [seed]`
"""
import random
import sys
from typing import List
from priority_queue import Task, MaxHeap


def run_simulation(num_tasks: int = 100, seed: int = 1) -> dict:
    random.seed(seed)
    tasks: List[Task] = []
    time = 0.0
    for i in range(num_tasks):
        inter = random.expovariate(1 / 5)
        time += inter
        priority = random.randint(1, 100)
        deadline = time + random.uniform(1, 20)
        tasks.append(Task(i, priority=priority, arrival=time, deadline=deadline))

    tasks.sort(key=lambda t: t.arrival)

    pq = MaxHeap()
    now = 0.0
    idx = 0
    served = 0
    total_wait = 0.0
    missed = 0

    while idx < len(tasks) or not pq.is_empty():
        if pq.is_empty() and idx < len(tasks):
            now = max(now, tasks[idx].arrival)

        while idx < len(tasks) and tasks[idx].arrival <= now:
            pq.insert(tasks[idx])
            idx += 1

        job = pq.extract_max()
        if job is None:
            continue
        wait = now - job.arrival
        total_wait += wait
        served += 1
        now += 1.0
        if job.deadline is not None and now > job.deadline:
            missed += 1

    return {"served": served, "avg_wait": (total_wait / served) if served else 0.0, "missed_deadlines": missed}


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 42
    res = run_simulation(n, seed)
    print(res)
