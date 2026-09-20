"""Seeded workload generation and paired, repeated policy comparisons."""

import random
import statistics
from .engine import compare, integer

PROFILES = ("mixed", "batch", "interactive", "convoy")


def generate(seed=42, count=12, profile="mixed"):
    integer(seed, "seed", 0, 2147483647)
    integer(count, "count", 2, 100)
    if not isinstance(profile, str) or profile not in PROFILES:
        raise ValueError("Unknown workload profile")
    rng = random.Random(seed)
    rows = []
    for i in range(count):
        if profile == "batch":
            arrival, burst = 0, rng.randint(10, 40)
        elif profile == "interactive":
            arrival, burst = rng.randint(0, count * 2), rng.randint(1, 6)
        elif profile == "convoy":
            arrival, burst = (0, 60) if i == 0 else (rng.randint(1, 5), rng.randint(1, 4))
        else:
            arrival, burst = rng.randint(0, count * 2), rng.randint(1, 5) if rng.random() < .7 else rng.randint(15, 40)
        rows.append({"id": f"P{i + 1}", "arrival": arrival, "burst": burst, "priority": rng.randint(0, 9)})
    return rows


def benchmark(seed=42, count=20, profile="mixed", repeats=10, quantum=3):
    integer(repeats, "repeats", 2, 30)
    integer(seed, "seed", 0, 2147483647 - repeats)
    samples = []
    aggregates = {}
    for offset in range(repeats):
        results = compare(generate(seed + offset, count, profile), quantum)
        for result in results:
            metrics = result["metrics"]
            samples.append({"seed": seed + offset, "algorithm": result["algorithm"], **metrics})
            for key in ("mean_waiting", "mean_response", "mean_turnaround", "p95_waiting", "context_switches"):
                aggregates.setdefault(result["algorithm"], {}).setdefault(key, []).append(metrics[key])
    summary = []
    for algorithm, metrics in aggregates.items():
        summary.append({"algorithm": algorithm, "metrics": {
            key: {"mean": statistics.mean(values), "stddev": statistics.stdev(values),
                  "min": min(values), "max": max(values)} for key, values in metrics.items()}})
    return {"config": {"seed": seed, "count": count, "profile": profile, "repeats": repeats, "quantum": quantum},
            "summary": summary, "samples": samples}
