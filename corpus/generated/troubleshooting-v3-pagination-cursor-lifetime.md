---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: pagination cursor lifetime (Kestrel v3)

Problems with the pagination cursor lifetime are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different pagination cursor lifetime from the one you set.
- The log shows `E1872: KESTREL_PAGINATION_CURSOR_LIFETIME out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 1 to 87 percent. Out of range, the value is rejected with `E1872: KESTREL_PAGINATION_CURSOR_LIFETIME out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_PAGINATION_CURSOR_LIFETIME` to see the value in use.

## Check 2: has it taken effect?

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `pagination_cursor_lifetime`. In version 3 it is warned. The setting that counts is `KESTREL_PAGINATION_CURSOR_LIFETIME`, and its default is 23 percent.

## What the metrics show

The service exports the metric `kestrel_pagination_cursor_lifetime_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
