---
product: Kestrel Data Runner
version: v2
section: Troubleshooting
---

# Troubleshooting: trace sampling rate (Kestrel v2)

Problems with the trace sampling rate are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different trace sampling rate from the one you set.
- The log shows `E1262: trace_sampling_rate_min out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 5 to 219 minutes. Out of range, the value is rejected with `E1262: trace_sampling_rate_min out of range` and the previous value stays in force. Run `kestrelctl config show trace_sampling_rate_min` to see the value in use.

## Check 2: has it taken effect?

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Check 3: is it set in the right place?

In version 2 the setting lives in `kestrel.conf`, in the `[jobs]` block. A value set anywhere else is not read.

## What the metrics show

Watch `kestrel_trace_sampling_rate_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
