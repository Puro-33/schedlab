# Provenance and extension boundary

Upstream: https://github.com/SorawitChok/Process-Scheduling-Simulation-Project

Starting commit: `f7b2f98fa4fd5875dd443414b1d05fc18500459a`.

Original authors: Sorawit Chokphantavee, Sirawit Chokphantavee, Narinthorn Chinvorarat, Nathanon Rookheb. Original license: MIT (2024); the complete notice is retained unchanged in the repository root.

The original `simulator.py` and `img/` files are unchanged. Its README is preserved in `docs/UPSTREAM_README.md`. The original Git history remains the ancestry of this extension. Run `git log --oneline --all` to inspect it.

The `schedlab/`, `web/`, `tests/`, `scripts/`, CI workflow, and new documentation are SchedLab additions. The web engine was written independently and does not call the desktop GUI. This creates a testable service boundary while retaining the original project as a documented baseline.

## Concrete connection to the upstream implementation

`tests/test_upstream.py` extracts only three inspected function definitions with Python's AST library; it does not launch Tkinter or execute module-level code. It verifies SchedLab SJF's timeline against `SJF_NON2` for the upstream README's five-process example. It also records a metric difference: upstream `Respond([[1, 5, 7]])` returns 5 (absolute start), while a job arriving at 5 and starting at 5 correctly has response time 0 in SchedLab.

The original response function is preserved for provenance, not silently changed. The corrected metric is part of the new engine. No general correctness guarantee is made for the legacy GUI or all legacy policies. The web version has separate hand-computed tests, an independent SRTF oracle, and service-conservation checks.

## New work

1. Six-policy deterministic event-driven simulation, with named validation and tie rules.
2. Seeded workload generation and paired repeat experiments.
3. Responsive browser UI, interactive replay, comparison, and import/export.
4. SQLite persistence and a bounded local API.
5. Automated algorithm/API/browser verification and CI.
6. Reproducible 1,440-measurement study with limitations and a defense guide.

AI assistance was used to implement and document the extension. Students presenting this project should disclose assistance according to their institution's rules and be able to explain and modify the algorithms and experiments themselves.
