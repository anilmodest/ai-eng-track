---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: notification digest interval (Kestrel v3)

Problems with the notification digest interval are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different notification digest interval from the one you set.
- The log shows `E1664: KESTREL_NOTIFICATION_DIGEST_INTERVAL out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 20 to 3846 characters. Out of range, the value is rejected with `E1664: KESTREL_NOTIFICATION_DIGEST_INTERVAL out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_NOTIFICATION_DIGEST_INTERVAL` to see the value in use.

## Check 2: has it taken effect?

The value is reloaded within a few seconds of being changed. No restart is needed, and work already in progress picks up the new value on its next step.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `notification_digest_interval`. In version 3 it is ignored. The setting that counts is `KESTREL_NOTIFICATION_DIGEST_INTERVAL`, and its default is 597 characters.

## What the metrics show

The service exports the metric `kestrel_notification_digest_interval_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
