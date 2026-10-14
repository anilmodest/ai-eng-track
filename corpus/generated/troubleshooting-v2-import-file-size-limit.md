---
product: Kestrel Data Runner
version: v2
section: Troubleshooting
---

# Troubleshooting: import file size limit (Kestrel v2)

Problems with the import file size limit are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different import file size limit from the one you set.
- The log shows `E1478: import_file_size_limit_day out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 18 to 3358 days. Out of range, the value is rejected with `E1478: import_file_size_limit_day out of range` and the previous value stays in force. Run `kestrelctl config show import_file_size_limit_day` to see the value in use.

## Check 2: has it taken effect?

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Check 3: is it set in the right place?

In version 2 the setting lives in `kestrel.conf`, in the `[network]` block. A value set anywhere else is not read.

## What the metrics show

The service exports the metric `kestrel_import_file_size_limit_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
