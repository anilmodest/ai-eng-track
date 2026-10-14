---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: field length limit (Kestrel v3)

Problems with the field length limit are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different field length limit from the one you set.
- The log shows `E1807: KESTREL_FIELD_LENGTH_LIMIT out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 1 to 79 percent. Out of range, the value is rejected with `E1807: KESTREL_FIELD_LENGTH_LIMIT out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_FIELD_LENGTH_LIMIT` to see the value in use.

## Check 2: has it taken effect?

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `field_length_limit`. In version 3 it is rejected. The setting that counts is `KESTREL_FIELD_LENGTH_LIMIT`, and its default is 22 percent.

## What the metrics show

The service exports the metric `kestrel_field_length_limit_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
