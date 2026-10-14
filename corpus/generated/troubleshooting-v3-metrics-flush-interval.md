---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: metrics flush interval (Kestrel v3)

Start here when the metrics flush interval does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different metrics flush interval from the one you set.
- The log shows `E1779: KESTREL_METRICS_FLUSH_INTERVAL out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 1 to 156 hours. Out of range, the value is rejected with `E1779: KESTREL_METRICS_FLUSH_INTERVAL out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_METRICS_FLUSH_INTERVAL` to see the value in use.

## Check 2: has it taken effect?

The value is reloaded within a few seconds of being changed. No restart is needed, and work already in progress picks up the new value on its next step.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `metrics_flush_interval`. In version 3 it is ignored. The setting that counts is `KESTREL_METRICS_FLUSH_INTERVAL`, and its default is 2 hours.

## What the metrics show

The service exports the metric `kestrel_metrics_flush_interval_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
