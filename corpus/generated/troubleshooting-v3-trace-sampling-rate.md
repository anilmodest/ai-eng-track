---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: trace sampling rate (Kestrel v3)

Problems with the trace sampling rate are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different trace sampling rate from the one you set.
- The log shows `E1262: KESTREL_TRACE_SAMPLING_RATE out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 1 to 224 minutes. Out of range, the value is rejected with `E1262: KESTREL_TRACE_SAMPLING_RATE out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_TRACE_SAMPLING_RATE` to see the value in use.

## Check 2: has it taken effect?

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `trace_sampling_rate_min`. In version 3 it is ignored. The setting that counts is `KESTREL_TRACE_SAMPLING_RATE`, and its default is 30 minutes.

## What the metrics show

The service exports the metric `kestrel_trace_sampling_rate_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
