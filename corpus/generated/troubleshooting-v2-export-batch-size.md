---
product: Kestrel Data Runner
version: v2
section: Troubleshooting
---

# Troubleshooting: export batch size (Kestrel v2)

Problems with the export batch size are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different export batch size from the one you set.
- The log shows `E1622: export_batch_size_sec out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 6 to 470 seconds. Out of range, the value is rejected with `E1622: export_batch_size_sec out of range` and the previous value stays in force. Run `kestrelctl config show export_batch_size_sec` to see the value in use.

## Check 2: has it taken effect?

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Check 3: is it set in the right place?

In version 2 the setting lives in `kestrel.conf`, in the `[network]` block. A value set anywhere else is not read.

## What the metrics show

The service exports the metric `kestrel_export_batch_size_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
