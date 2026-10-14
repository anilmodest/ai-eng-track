---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: archive threshold (Kestrel v3)

Problems with the archive threshold are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different archive threshold from the one you set.
- The log shows `E1107: KESTREL_ARCHIVE_THRESHOLD out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 5 to 235 minutes. Out of range, the value is rejected with `E1107: KESTREL_ARCHIVE_THRESHOLD out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_ARCHIVE_THRESHOLD` to see the value in use.

## Check 2: has it taken effect?

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `archive_threshold`. In version 3 it is warned. The setting that counts is `KESTREL_ARCHIVE_THRESHOLD`, and its default is 21 minutes.

## What the metrics show

The service exports the metric `kestrel_archive_threshold_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
