# Demonstration and oral defense

## Ten-minute demonstration

1. **Minute 0–1: Problem and prior work.** Open the upstream project link and explain the preserved baseline. Show the contribution table; identify the new engine, research workflow, storage, and UI.
2. **Minute 1–3: A concrete scheduling trace.** Import the fixture below. Compare FCFS, SJF, SRTF, and RR. Scrub SRTF to time 2 and explain why P3 preempts P2.
3. **Minute 3–4: Metric calculation.** For P1 under SRTF, completion is 14, arrival 0, burst 8: turnaround 14, waiting 6, response 0. Contrast with P2 and P3.
4. **Minute 4–6: Quantum tradeoff.** Generate the convoy profile, seed 42, eight processes. Compare RR quantum 1 and 8 using response time and context switches. Explain the zero-overhead assumption.
5. **Minute 6–7: Reproducibility.** Run a 10-repeat benchmark. Explain shared inputs, seeds, standard deviation, and why it is not a confidence interval. Export the raw samples.
6. **Minute 7–8: Persistence.** Save a named run, edit its burst, observe stale results disappear, and reload the saved run. Export its JSON and CSV.
7. **Minute 8–9: Evidence.** Run the unit tests. Show the independent SRTF oracle and the upstream response-time regression.
8. **Minute 9–10: Limits and next work.** Explain known bursts, finite arrivals, single core, no I/O, and no switch duration. Propose a scoped extension.

Importable fixture:

```json
{"quantum": 2, "processes": [
  {"id": "P1", "arrival": 0, "burst": 8, "priority": 2},
  {"id": "P2", "arrival": 1, "burst": 4, "priority": 1},
  {"id": "P3", "arrival": 2, "burst": 2, "priority": 0}
]}
```

## Questions to be ready for

**What did you add to the original repository?**
The testable event-driven web engine, Priority and HRRN, corrected arrival-relative response, six-policy comparisons, reproducible repeated workloads, SQLite notebook, exports, automated verification, and evaluation report. The original GUI and authorship are explicitly preserved.

**Why is response different from waiting?**
Response measures only the delay until first execution. Waiting includes every period spent ready but not running, including interruptions after the first execution.

**Why not always choose SRTF?**
It assumes remaining CPU demand is known, prioritizes short jobs, and may perform more switches. A system can care about response, fairness, deadlines, or predictability. Infinite arrival streams require a separate starvation analysis.

**How do simultaneous events work?**
Arrivals at a quantum endpoint are enqueued before the unfinished RR job. Score ties resolve by arrival, then original input order. These choices are documented and tested.

**How do you know the engine is correct?**
Hand-derived examples, source-level SJF baseline comparison, a separate time-step SRTF implementation, conservation invariants across generated workloads, and integration tests. These supply evidence without proving every possible input mathematically.

**Why do utilization and makespan often match across policies?**
Each policy executes the same total work on one CPU without switching cost or I/O and never idles while a job is ready. Scheduling order changes who waits, but not the total busy work.

**Why use SQLite and plain JavaScript?**
The research artifact runs locally without external services or Python dependencies. Persistence and visualization are separated from the algorithms, so they can be replaced without changing scheduling semantics.

**What does mean ± standard deviation mean?**
It summarizes the distribution across the generated workloads. It does not quantify a confidence interval for a population mean and does not by itself demonstrate statistical significance.

**What would make this stronger as a thesis?**
An approved new research question, realistic workload traces, a richer overhead/I/O model, formal reasoning about policy behavior, and statistical analysis designed before evaluating the new method.
