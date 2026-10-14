---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: dead-letter retention (Kestrel v3)

Problems with the dead-letter retention are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different dead-letter retention from the one you set.
- The log shows `E1260: KESTREL_DEAD_LETTER_RETENTION out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 12 to 580 seconds. Out of range, the value is rejected with `E1260: KESTREL_DEAD_LETTER_RETENTION out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_DEAD_LETTER_RETENTION` to see the value in use.

## Check 2: has it taken effect?

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `dead_letter_retention`. In version 3 it is ignored. The setting that counts is `KESTREL_DEAD_LETTER_RETENTION`, and its default is 149 seconds.

## What the metrics show

The service exports the metric `kestrel_dead_letter_retention_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
