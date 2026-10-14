---
product: Kestrel Data Runner
version: v2
section: Troubleshooting
---

# Troubleshooting: attachment size limit (Kestrel v2)

Problems with the attachment size limit are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different attachment size limit from the one you set.
- The log shows `E1894: attachment_size_limit out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 23 to 3641 days. Out of range, the value is rejected with `E1894: attachment_size_limit out of range` and the previous value stays in force. Run `kestrelctl config show attachment_size_limit` to see the value in use.

## Check 2: has it taken effect?

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Check 3: is it set in the right place?

In version 2 the setting lives in `kestrel.conf`, in the `[security]` block. A value set anywhere else is not read.

## What the metrics show

Watch `kestrel_attachment_size_limit_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
