# Contributing to SchedLab

Keep policy code independent of HTTP, SQLite, and the browser. Document tie-breaking, arrival order, and metric definitions when changing behavior.

For an algorithm change, supply a hand-calculated fixture or independent reference check and run `python3 -m unittest discover -s tests -v`. For browser changes, run `npm ci`, `npx playwright install chromium`, and `npm run test:browser`. The application itself requires no npm packages.

Reproduce evaluation data with `python3 -m scripts.research`. Changes to the generator or simulation semantics require updating the report and explaining why previous results differ. Do not treat duplicated baseline runs at different RR quantum settings as independent statistical evidence.

Preserve upstream attribution, the license, and the original source. Prefer extending the web package rather than altering the archived desktop baseline. Do not commit local SQLite data, credentials, virtual environments, or installed dependencies.
