"""Reproduce the committed benchmark report: python3 -m scripts.research."""

import csv
import json
from pathlib import Path
from schedlab.experiments import benchmark


def main():
    target = Path(__file__).resolve().parent.parent / "docs" / "results"
    target.mkdir(parents=True, exist_ok=True)
    experiments = [benchmark(seed=100, count=25, profile=profile, repeats=20, quantum=q)
                   for profile in ("mixed", "batch", "interactive", "convoy") for q in (1, 3, 8)]
    (target / "benchmarks.json").write_text(json.dumps(experiments, indent=2) + "\n")
    rows = [{"profile": result["config"]["profile"], "quantum": result["config"]["quantum"], **sample}
            for result in experiments for sample in result["samples"]]
    with (target / "samples.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    lines = ["# Reproducible benchmark results", "",
             "Generated with `python3 -m scripts.research`. Each cell is the mean across 20 paired workloads (seeds 100–119), 25 processes each. Times are abstract simulation units; context switches have zero duration.", "",
             "| Profile | Quantum | Policy | Mean waiting | Mean response | Mean turnaround | Switches |",
             "|---|---:|---|---:|---:|---:|---:|"]
    for result in experiments:
        for row in result["summary"]:
            m = row["metrics"]
            cells = [result["config"]["profile"], str(result["config"]["quantum"]), row["algorithm"]]
            cells.extend(f"{m[key]['mean']:.2f}" for key in ("mean_waiting", "mean_response", "mean_turnaround", "context_switches"))
            lines.append("| " + " | ".join(cells) + " |")
    lines.extend(["", "Raw samples and sample standard deviations are in `benchmarks.json`; flattened samples are in `samples.csv`. Repeated deterministic baselines across quantum settings are intentional controls, not independent observations.", ""])
    (target / "RESULTS.md").write_text("\n".join(lines))
    print(f"Wrote {len(rows)} policy measurements to {target}")


if __name__ == "__main__":
    main()
