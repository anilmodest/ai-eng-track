---
product: Kestrel Data Runner
version: v3
section: Operations
---

# Scheduling runs (Kestrel v3)

A schedule tells Kestrel when to start a run without anyone asking for it.

## How schedules are written

Schedules are set per pipeline in the console, or through `KESTREL_SCHEDULE`, as an ISO-8601 repeating interval with an explicit timezone.

```
export KESTREL_SCHEDULE='R/2026-01-01T02:00:00[Europe/London]/P1D'
```

Cron expressions are **no longer accepted**. A `schedules.conf` left in place is ignored and the pipeline simply never runs on a schedule, with no error, which is the usual reason scheduled runs stop after an upgrade.

## Overlap

If a scheduled run is still going when the next one is due, the next one is **queued** and starts when the first finishes. At most one run is queued; further ones are dropped with a warning.

## Catching up

Runs missed while the runner was stopped are started once when it comes back, unless `KESTREL_SCHEDULE_CATCHUP=false`.
