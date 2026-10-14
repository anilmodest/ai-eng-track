---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: webhook retry count (Kestrel v3)

Problems with the webhook retry count are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different webhook retry count from the one you set.
- The log shows `E1725: KESTREL_WEBHOOK_RETRY_COUNT out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 2 to 86 percent. Out of range, the value is rejected with `E1725: KESTREL_WEBHOOK_RETRY_COUNT out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_WEBHOOK_RETRY_COUNT` to see the value in use.

## Check 2: has it taken effect?

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `webhook_retry_count`. In version 3 it is warned. The setting that counts is `KESTREL_WEBHOOK_RETRY_COUNT`, and its default is 18 percent.

## What the metrics show

Watch `kestrel_webhook_retry_count_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
