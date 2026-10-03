---
product: Kestrel Data Runner
version: v2
section: Operations
---

# Scheduling runs (Kestrel v2)

A schedule tells Kestrel when to start a run without anyone asking for it.

## How schedules are written

Schedules live in `schedules.conf`, one per line, as a five-field cron expression followed by the pipeline name.

```
0 2 * * *  nightly-export
*/15 * * * *  inbox-poll
```

All times are interpreted in **UTC**. There is no timezone setting; a team that wants 2am local must work out the UTC equivalent and change it twice a year.

## Overlap

If a scheduled run is still going when the next one is due, the next one is **skipped** and a warning is written to the log.

## Catching up

Runs missed while the runner was stopped are not started when it comes back.
