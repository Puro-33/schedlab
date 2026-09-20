# Reproducible Comparative Evaluation of CPU Scheduling Policies

## Abstract

SchedLab extends an existing open-source CPU scheduling simulator into a browser-based experiment platform. The implementation separates policy decisions from visualization, adds two policies, corrects arrival-relative response-time measurement, and supports paired comparisons over seeded synthetic workloads. The accompanying evaluation contains 1,440 policy measurements across four workload families and three Round Robin quantum settings. The measurements illustrate the response-time/turnaround tradeoff and the dependence of results on workload composition. They are simulation results, not operating-system performance measurements.

## Problem and objectives

A single Gantt chart helps explain an algorithm but gives weak evidence for choosing a policy. Manual process entry also makes repeated experiments difficult. This project asks:

1. How do FCFS, SJF, SRTF, RR, Priority, and HRRN differ on the same finite workload?
2. How does RR quantum affect initial response and the number of process transitions?
3. How does workload composition change the apparent best policy?
4. Can a student reproduce the results and inspect individual scheduling decisions?

The deliverable combines an algorithm implementation, an API, a database, an interactive client, automated verification, and a reproducible evaluation. Original research novelty is not claimed for these established scheduling algorithms.

## Relationship to prior work

The foundation is [SorawitChok/Process-Scheduling-Simulation-Project](https://github.com/SorawitChok/Process-Scheduling-Simulation-Project), a Tkinter/Turtle simulator with FCFS, SJF, preemptive SJF, and RR. Its original code and history are retained. SchedLab adds an independently implemented event-driven engine, Priority and HRRN, a browser UI, persistence, repeat experiments, and test automation. [Provenance](PROVENANCE.md) identifies preserved and added components.

The CPU scheduling discussion in [Operating Systems: Three Easy Pieces](https://pages.cs.wisc.edu/~remzi/OSTEP/cpu-sched.pdf) supplies the conceptual distinction between turnaround and response. The [University of Wisconsin scheduling notes](https://pages.cs.wisc.edu/~bart/537/lecturenotes/s11.html) discuss FCFS, Round Robin, preemption, and scheduling objectives.

## Requirements

| Requirement | Implementation | Verification |
|---|---|---|
| Deterministic policy comparison | `schedlab/engine.py` | Hand-calculated fixtures, tie and RR boundary tests |
| Accurate service and metrics | Per-process results and timeline | Service conservation, nonnegative waits, independent SRTF oracle |
| Reproducible workloads | `random.Random(seed)` local generator | Determinism and paired benchmark tests |
| Inspectable execution | Browser Gantt chart and scrubber | Browser policy selection and playback checks |
| Save and reload | SQLite notebook | API round-trip and browser persistence tests |
| Export and import | JSON run and benchmark exports; CSV process metrics | Browser download parsing and import validation |
| Upstream continuity | Preserved source, license, Git ancestry | SJF compatibility fixture and response regression |

## Design

The HTTP layer accepts JSON, validates workload inputs, and calls pure simulation functions. The browser keeps the editable workload separate from the last completed run. Editing process data invalidates the displayed results and disables saving, avoiding the accidental association of old results with a new input.

Each simulation maintains a sorted arrival list, an eligible queue, remaining burst lengths, first-start times, completion times, and a compressed timeline. Time advances to dispatch completion, quantum expiry, the next relevant arrival, or the end of an idle gap. The SRTF engine never scans all empty time ticks; it reevaluates at arrival events. Ready-policy selection is linear for simplicity and inspectability.

SQLite stores an experiment ID, name, UTC creation timestamp, and a JSON payload containing input, quantum, computed outputs, and engine version. The database uses parameterized queries and one transaction-scoped connection per operation. No remote data services or model API keys are required.

## Policy definitions

| Policy | Selection | Preemptive? |
|---|---|---|
| FCFS | Earliest arrival, then input position | No |
| SJF | Smallest original burst among arrived jobs | No |
| SRTF | Smallest remaining burst at arrival events | Yes |
| RR | FIFO ready queue, fixed quantum | Yes |
| Priority | Smallest numeric priority, then arrival/input order | No |
| HRRN | Largest `(waiting + burst) / burst`, then arrival/input order | No |

For equal SRTF remaining times, arrival then input position resolves the tie, even if that changes the running job. RR adds all jobs arriving through the endpoint before requeuing an unfinished job. Adjacent segments with the same process ID are merged visually. A dispatch is a selection event; it need not be a switch to a different process.

Let `n` be the number of processes, `B` their total burst, and `q` the RR quantum. Arrival sorting costs `O(n log n)`. FCFS is linear after sorting; RR has `O(n + B/q)` dispatches plus arrival sorting. SJF, HRRN, and Priority use `O(n²)` selection. SRTF has at most linear-many arrival/completion decision events and `O(n²)` selection in this implementation. Memory is `O(n + s)` for `s` stored timeline segments. Request limits are 100 processes, 20,000 total burst units, and arrival values no greater than 10,000.

## Metrics

For process `i`, let `aᵢ` = arrival, `bᵢ` = burst, `sᵢ` = first start, and `cᵢ` = completion:

- Turnaround: `cᵢ − aᵢ`.
- Waiting: `cᵢ − aᵢ − bᵢ`.
- Response: `sᵢ − aᵢ`.
- Slowdown: `(cᵢ − aᵢ) / bᵢ`.
- Makespan: `max(cᵢ)`, measured from time zero.
- Utilization: `sum(bᵢ) / makespan`.
- Throughput: `n / makespan`.
- P95 waiting: nearest-rank percentile, sorted waits at index `ceil(0.95n) − 1`.
- Context switches: transitions between distinct running processes, excluding first dispatch and idle gaps.

## Evaluation protocol

Run `python3 -m scripts.research` from the repository root. The script creates Markdown, CSV, and JSON in `docs/results/`.

Fixed design: 25 jobs, seeds 100–119, RR quantum 1/3/8, six policies, four profiles. Each seed/profile combination defines a workload reused by all policies and all quantum settings. There are 80 distinct workloads and 1,440 policy executions. Duplicate deterministic baseline measurements at different quantum settings are controls, not additional independent observations.

Profiles:

- **Mixed:** arrivals uniform in `[0, 2n]`; 70% short bursts in `[1, 5]`, otherwise `[15, 40]`.
- **Batch:** all arrivals at 0; bursts uniform in `[10, 40]`.
- **Interactive:** arrivals uniform in `[0, 2n]`; bursts uniform in `[1, 6]`. This models short CPU jobs, not I/O interactivity.
- **Convoy:** one burst of 60 at time 0; other jobs arrive in `[1, 5]` with bursts in `[1, 4]`.

Priorities are independently drawn from `[0, 9]`. No policy is tuned against the evaluation seeds. Summaries report arithmetic means and sample standard deviations across workloads. They are descriptive statistics, not confidence intervals or significance tests. Exported raw samples permit a separate paired statistical analysis.

## Observed results

The generated [results table](results/RESULTS.md) and [raw samples](results/samples.csv) are authoritative. For the mixed profile:

| Policy / quantum | Mean waiting | Mean response | Mean turnaround | Mean switches |
|---|---:|---:|---:|---:|
| FCFS | 100.58 | 100.58 | 110.96 | 23.60 |
| SJF | 45.64 | 45.64 | 56.02 | 23.60 |
| SRTF | 38.53 | 35.21 | 48.91 | 27.15 |
| RR / 1 | 81.23 | 7.12 | 91.61 | 251.40 |
| RR / 3 | 82.45 | 19.05 | 92.83 | 92.90 |
| RR / 8 | 86.91 | 39.31 | 97.29 | 44.90 |
| HRRN | 50.31 | 50.31 | 60.69 | 23.60 |

Here, SRTF has lower average waiting and turnaround than the other evaluated policies. RR with quantum 1 reaches jobs earlier but performs substantially more process transitions. Increasing quantum reduces those transitions while worsening initial response on this sample. Since context-switch duration is zero, these results cannot quantify the elapsed-time cost of those additional switches.

All policies are work-conserving under this model, so utilization and makespan are not useful policy differentiators for a shared workload with no switch overhead or I/O. The dashboard includes them to explain the trace and idle periods, not to imply differences that the model cannot produce.

## Validation and limitations

The test suite includes hand-computed completion times, idle gaps, stable ties, quantum-boundary arrivals, input rejection, reproducibility, HTTP persistence, and source-level comparison with the upstream SJF example. An independently written tick-by-tick SRTF oracle verifies completion times across generated inputs. Randomized invariant checks cover all policies, but only SRTF currently has an independent full-policy oracle. Browser tests verify main user workflows, exported file contents, and absence of mobile page overflow.

The model assumes known burst lengths, no I/O, one core, zero switching cost, no deadlines, finite arrivals, and no cache effects. Finite workloads cannot establish starvation freedom for an infinite stream of jobs. Synthetic distributions may not represent real production traces. The local HTTP server has no multi-user authentication or production deployment guarantees. The legacy desktop application is retained unchanged and its GUI is not covered by new browser tests.

## Further research

Potential student extensions include explicit context-switch time, I/O blocking, MLFQ with periodic priority boosts, measured trace ingestion, paired confidence intervals, and a discrete-event multicore model. Each should add a specified model, reference fixtures, and new experiments before making comparative claims.
