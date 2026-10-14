---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: attachment size limit (Kestrel v3)

Start here when the attachment size limit does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different attachment size limit from the one you set.
- The log shows `E1894: KESTREL_ATTACHMENT_SIZE_LIMIT out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 46 to 3628 days. Out of range, the value is rejected with `E1894: KESTREL_ATTACHMENT_SIZE_LIMIT out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_ATTACHMENT_SIZE_LIMIT` to see the value in use.

## Check 2: has it taken effect?

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `attachment_size_limit`. In version 3 it is rejected. The setting that counts is `KESTREL_ATTACHMENT_SIZE_LIMIT`, and its default is 499 days.

## What the metrics show

The service exports the metric `kestrel_attachment_size_limit_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
