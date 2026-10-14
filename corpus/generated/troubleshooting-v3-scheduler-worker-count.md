---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: scheduler worker count (Kestrel v3)

Start here when the scheduler worker count does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different scheduler worker count from the one you set.
- The log shows `E1929: KESTREL_SCHEDULER_WORKER_COUNT out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 2 to 238 minutes. Out of range, the value is rejected with `E1929: KESTREL_SCHEDULER_WORKER_COUNT out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_SCHEDULER_WORKER_COUNT` to see the value in use.

## Check 2: has it taken effect?

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `scheduler_worker_count`. In version 3 it is rejected. The setting that counts is `KESTREL_SCHEDULER_WORKER_COUNT`, and its default is 28 minutes.

## What the metrics show

The service exports the metric `kestrel_scheduler_worker_count_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
