---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: transform memory limit (Kestrel v3)

Problems with the transform memory limit are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different transform memory limit from the one you set.
- The log shows `E1915: KESTREL_TRANSFORM_MEMORY_LIMIT out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 10 to 400 connections. Out of range, the value is rejected with `E1915: KESTREL_TRANSFORM_MEMORY_LIMIT out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_TRANSFORM_MEMORY_LIMIT` to see the value in use.

## Check 2: has it taken effect?

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `transform_memory_limit`. In version 3 it is ignored. The setting that counts is `KESTREL_TRANSFORM_MEMORY_LIMIT`, and its default is 19 connections.

## What the metrics show

The service exports the metric `kestrel_transform_memory_limit_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
