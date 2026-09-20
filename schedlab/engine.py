"""Deterministic, event-driven scheduling with integer time units.

Single CPU, one known CPU burst per process, no I/O or dispatch cost.
Ties use arrival time then input position. RR admits arrivals at the end
of a quantum before re-enqueuing the interrupted process.
"""

from collections import deque
from dataclasses import dataclass
from math import ceil, fsum
import re

ALGORITHMS = {
    "fcfs": "First Come First Served",
    "sjf": "Shortest Job First",
    "srtf": "Shortest Remaining Time First",
    "rr": "Round Robin",
    "priority": "Non-preemptive Priority",
    "hrrn": "Highest Response Ratio Next",
}


def integer(value, name, minimum, maximum):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer from {minimum} to {maximum}")
    return value


@dataclass(frozen=True)
class Process:
    id: str
    arrival: int
    burst: int
    priority: int = 0


def validate_processes(rows):
    if not isinstance(rows, list) or not 1 <= len(rows) <= 100:
        raise ValueError("Provide 1–100 processes")
    processes = []
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Each process must be an object")
        pid = row.get("id")
        if not isinstance(pid, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,24}", pid):
            raise ValueError("Process IDs must use 1–24 letters, digits, underscores or hyphens")
        if pid in seen:
            raise ValueError(f"Duplicate process ID: {pid}")
        seen.add(pid)
        processes.append(Process(pid, integer(row.get("arrival"), "arrival", 0, 10000),
                                 integer(row.get("burst"), "burst", 1, 1000),
                                 integer(row.get("priority", 0), "priority", 0, 99)))
    if sum(p.burst for p in processes) > 20000:
        raise ValueError("Total CPU burst must not exceed 20000 time units")
    return processes


def simulate(rows, algorithm="fcfs", quantum=3):
    processes = validate_processes(rows)
    if not isinstance(algorithm, str) or algorithm not in ALGORITHMS:
        raise ValueError("Unknown scheduling algorithm")
    quantum = integer(quantum, "quantum", 1, 1000)
    n = len(processes)
    pending = sorted(range(n), key=lambda i: (processes[i].arrival, i))
    ready = deque()
    remaining = [p.burst for p in processes]
    first = [None] * n
    completion = [0] * n
    timeline = []
    time = cursor = done = dispatches = switches = 0
    previous = None

    def admit():
        nonlocal cursor
        while cursor < n and processes[pending[cursor]].arrival <= time:
            ready.append(pending[cursor])
            cursor += 1

    def segment(pid, start, end):
        if timeline and timeline[-1]["id"] == pid and timeline[-1]["end"] == start:
            timeline[-1]["end"] = end
        else:
            timeline.append({"id": pid, "start": start, "end": end})

    while done < n:
        admit()
        if not ready:
            next_time = processes[pending[cursor]].arrival
            segment(None, time, next_time)
            time = next_time
            previous = None
            admit()
        if algorithm in ("fcfs", "rr"):
            i = ready.popleft()
        else:
            def key(index):
                p = processes[index]
                score = {"sjf": p.burst, "srtf": remaining[index],
                         "priority": p.priority,
                         "hrrn": -(time - p.arrival + p.burst) / p.burst}[algorithm]
                return score, p.arrival, index
            i = min(ready, key=key)
            ready.remove(i)
        dispatches += 1
        if previous is not None and previous != i:
            switches += 1
        previous = i
        if first[i] is None:
            first[i] = time
        duration = min(remaining[i], quantum) if algorithm == "rr" else remaining[i]
        if algorithm == "srtf" and cursor < n:
            duration = min(duration, processes[pending[cursor]].arrival - time)
        segment(processes[i].id, time, time + duration)
        time += duration
        remaining[i] -= duration
        admit()
        if remaining[i]:
            ready.append(i)
        else:
            completion[i] = time
            done += 1

    result = []
    for i, p in enumerate(processes):
        turnaround = completion[i] - p.arrival
        result.append({"id": p.id, "arrival": p.arrival, "burst": p.burst,
                       "priority": p.priority, "start": first[i], "completion": completion[i],
                       "turnaround": turnaround, "waiting": turnaround - p.burst,
                       "response": first[i] - p.arrival, "slowdown": turnaround / p.burst})
    waits = sorted(p["waiting"] for p in result)
    metrics = {"mean_" + metric: fsum(p[metric] for p in result) / n
               for metric in ("waiting", "turnaround", "response", "slowdown")}
    metrics.update({"p95_waiting": waits[ceil(.95 * n) - 1], "max_waiting": max(waits),
                    "makespan": time, "utilization": sum(p.burst for p in processes) / time,
                    "throughput": n / time, "context_switches": switches, "dispatches": dispatches})
    return {"algorithm": algorithm, "label": ALGORITHMS[algorithm], "quantum": quantum,
            "metrics": metrics, "processes": result, "timeline": timeline}


def compare(rows, quantum=3):
    return [simulate(rows, algorithm, quantum) for algorithm in ALGORITHMS]
