# Local API

Base address: `http://127.0.0.1:8080`. POST requests use `Content-Type: application/json`; request bodies are limited to 65,536 bytes. Host and optional Origin must match the local application address. No CORS access is exposed.

| Method | Path | Behavior |
|---|---|---|
| GET | `/api/health` | Status and policy names |
| POST | `/api/generate` | Seeded process list |
| POST | `/api/compare` | All six policy traces and metrics |
| POST | `/api/benchmark` | Repeated paired samples and summaries |
| GET | `/api/experiments` | Most recent 100 experiment records |
| POST | `/api/experiments` | Validate, recompute, and save a run |
| GET | `/api/experiments/{id}` | Saved input, settings, and results |

Generate or benchmark configuration:

```json
{"seed":42,"count":20,"profile":"mixed","quantum":3,"repeats":10}
```

`generate` uses seed/count/profile. `benchmark` also uses quantum/repeats. Profiles: `mixed`, `batch`, `interactive`, `convoy`. Count is 2–100; repetitions are 2–30. Benchmark seeds must allow the whole consecutive range to fit within the accepted 32-bit positive range.

Compare payload:

```json
{"quantum":2,"processes":[
  {"id":"P1","arrival":0,"burst":8,"priority":2},
  {"id":"P2","arrival":1,"burst":4,"priority":1},
  {"id":"P3","arrival":2,"burst":2,"priority":0}
]}
```

Saving accepts the same payload plus `name` (1–80 characters). Inputs are validated and results recomputed server-side. Clients cannot submit fabricated stored metrics.

```bash
curl http://127.0.0.1:8080/api/compare \
  -H 'Content-Type: application/json' \
  --data '{"quantum":2,"processes":[{"id":"P1","arrival":0,"burst":8},{"id":"P2","arrival":1,"burst":4}]}'
```

Each result contains `algorithm`, `label`, `quantum`, `metrics`, `processes`, and `timeline`. Timeline objects have `id`, `start`, `end`; idle segments have a null ID. Intervals are half-open: `[start, end)`.

Errors use `{"error":"explanation"}`: 400 invalid input, 403 disallowed host/origin, 404 missing route/record, 413 request length, 415 media type, 503 storage failure. The application is intended for one trusted local user and should not be exposed publicly without a separate production server, authentication, and deployment review.
