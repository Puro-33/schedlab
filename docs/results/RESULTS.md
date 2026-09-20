# Reproducible benchmark results

Generated with `python3 -m scripts.research`. Each cell is the mean across 20 paired workloads (seeds 100–119), 25 processes each. Times are abstract simulation units; context switches have zero duration.

| Profile | Quantum | Policy | Mean waiting | Mean response | Mean turnaround | Switches |
|---|---:|---|---:|---:|---:|---:|
| mixed | 1 | fcfs | 100.58 | 100.58 | 110.96 | 23.60 |
| mixed | 1 | sjf | 45.64 | 45.64 | 56.02 | 23.60 |
| mixed | 1 | srtf | 38.53 | 35.21 | 48.91 | 27.15 |
| mixed | 1 | rr | 81.23 | 7.12 | 91.61 | 251.40 |
| mixed | 1 | priority | 107.29 | 107.29 | 117.67 | 23.60 |
| mixed | 1 | hrrn | 50.31 | 50.31 | 60.69 | 23.60 |
| mixed | 3 | fcfs | 100.58 | 100.58 | 110.96 | 23.60 |
| mixed | 3 | sjf | 45.64 | 45.64 | 56.02 | 23.60 |
| mixed | 3 | srtf | 38.53 | 35.21 | 48.91 | 27.15 |
| mixed | 3 | rr | 82.45 | 19.05 | 92.83 | 92.90 |
| mixed | 3 | priority | 107.29 | 107.29 | 117.67 | 23.60 |
| mixed | 3 | hrrn | 50.31 | 50.31 | 60.69 | 23.60 |
| mixed | 8 | fcfs | 100.58 | 100.58 | 110.96 | 23.60 |
| mixed | 8 | sjf | 45.64 | 45.64 | 56.02 | 23.60 |
| mixed | 8 | srtf | 38.53 | 35.21 | 48.91 | 27.15 |
| mixed | 8 | rr | 86.91 | 39.31 | 97.29 | 44.90 |
| mixed | 8 | priority | 107.29 | 107.29 | 117.67 | 23.60 |
| mixed | 8 | hrrn | 50.31 | 50.31 | 60.69 | 23.60 |
| batch | 1 | fcfs | 309.94 | 309.94 | 335.29 | 24.00 |
| batch | 1 | sjf | 242.52 | 242.52 | 267.86 | 24.00 |
| batch | 1 | srtf | 242.52 | 242.52 | 267.86 | 24.00 |
| batch | 1 | rr | 479.20 | 12.00 | 504.55 | 632.10 |
| batch | 1 | priority | 302.64 | 302.64 | 327.99 | 24.00 |
| batch | 1 | hrrn | 248.40 | 248.40 | 273.74 | 24.00 |
| batch | 3 | fcfs | 309.94 | 309.94 | 335.29 | 24.00 |
| batch | 3 | sjf | 242.52 | 242.52 | 267.86 | 24.00 |
| batch | 3 | srtf | 242.52 | 242.52 | 267.86 | 24.00 |
| batch | 3 | rr | 478.61 | 36.00 | 503.96 | 218.30 |
| batch | 3 | priority | 302.64 | 302.64 | 327.99 | 24.00 |
| batch | 3 | hrrn | 248.40 | 248.40 | 273.74 | 24.00 |
| batch | 8 | fcfs | 309.94 | 309.94 | 335.29 | 24.00 |
| batch | 8 | sjf | 242.52 | 242.52 | 267.86 | 24.00 |
| batch | 8 | srtf | 242.52 | 242.52 | 267.86 | 24.00 |
| batch | 8 | rr | 472.60 | 96.00 | 497.95 | 88.10 |
| batch | 8 | priority | 302.64 | 302.64 | 327.99 | 24.00 |
| batch | 8 | hrrn | 248.40 | 248.40 | 273.74 | 24.00 |
| interactive | 1 | fcfs | 18.36 | 18.36 | 21.85 | 23.30 |
| interactive | 1 | sjf | 12.60 | 12.60 | 16.09 | 23.30 |
| interactive | 1 | srtf | 12.43 | 12.19 | 15.92 | 25.60 |
| interactive | 1 | rr | 24.32 | 5.87 | 27.81 | 82.95 |
| interactive | 1 | priority | 19.28 | 19.28 | 22.77 | 23.30 |
| interactive | 1 | hrrn | 14.79 | 14.79 | 18.28 | 23.30 |
| interactive | 3 | fcfs | 18.36 | 18.36 | 21.85 | 23.30 |
| interactive | 3 | sjf | 12.60 | 12.60 | 16.09 | 23.30 |
| interactive | 3 | srtf | 12.43 | 12.19 | 15.92 | 25.60 |
| interactive | 3 | rr | 21.87 | 13.54 | 25.36 | 35.40 |
| interactive | 3 | priority | 19.28 | 19.28 | 22.77 | 23.30 |
| interactive | 3 | hrrn | 14.79 | 14.79 | 18.28 | 23.30 |
| interactive | 8 | fcfs | 18.36 | 18.36 | 21.85 | 23.30 |
| interactive | 8 | sjf | 12.60 | 12.60 | 16.09 | 23.30 |
| interactive | 8 | srtf | 12.43 | 12.19 | 15.92 | 25.60 |
| interactive | 8 | rr | 18.36 | 18.36 | 21.85 | 23.30 |
| interactive | 8 | priority | 19.28 | 19.28 | 22.77 | 23.30 |
| interactive | 8 | hrrn | 14.79 | 14.79 | 18.28 | 23.30 |
| convoy | 1 | fcfs | 82.12 | 82.12 | 86.88 | 24.00 |
| convoy | 1 | sjf | 74.90 | 74.90 | 79.66 | 24.00 |
| convoy | 1 | srtf | 20.82 | 18.38 | 25.58 | 25.10 |
| convoy | 1 | rr | 36.39 | 10.76 | 41.15 | 64.15 |
| convoy | 1 | priority | 81.91 | 81.91 | 86.67 | 24.00 |
| convoy | 1 | hrrn | 74.90 | 74.90 | 79.66 | 24.00 |
| convoy | 3 | fcfs | 82.12 | 82.12 | 86.88 | 24.00 |
| convoy | 3 | sjf | 74.90 | 74.90 | 79.66 | 24.00 |
| convoy | 3 | srtf | 20.82 | 18.38 | 25.58 | 25.10 |
| convoy | 3 | rr | 36.00 | 25.61 | 40.76 | 32.85 |
| convoy | 3 | priority | 81.91 | 81.91 | 86.67 | 24.00 |
| convoy | 3 | hrrn | 74.90 | 74.90 | 79.66 | 24.00 |
| convoy | 8 | fcfs | 82.12 | 82.12 | 86.88 | 24.00 |
| convoy | 8 | sjf | 74.90 | 74.90 | 79.66 | 24.00 |
| convoy | 8 | srtf | 20.82 | 18.38 | 25.58 | 25.10 |
| convoy | 8 | rr | 34.56 | 32.20 | 39.31 | 25.00 |
| convoy | 8 | priority | 81.91 | 81.91 | 86.67 | 24.00 |
| convoy | 8 | hrrn | 74.90 | 74.90 | 79.66 | 24.00 |

Raw samples and sample standard deviations are in `benchmarks.json`; flattened samples are in `samples.csv`. Repeated deterministic baselines across quantum settings are intentional controls, not independent observations.
