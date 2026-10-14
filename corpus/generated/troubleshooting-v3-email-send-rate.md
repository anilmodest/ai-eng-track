---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: email send rate (Kestrel v3)

Start here when the email send rate does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different email send rate from the one you set.
- The log shows `E1229: KESTREL_EMAIL_SEND_RATE out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 50 to 8921 items. Out of range, the value is rejected with `E1229: KESTREL_EMAIL_SEND_RATE out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_EMAIL_SEND_RATE` to see the value in use.

## Check 2: has it taken effect?

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `email_send_rate`. In version 3 it is warned. The setting that counts is `KESTREL_EMAIL_SEND_RATE`, and its default is 2131 items.

## What the metrics show

Watch `kestrel_email_send_rate_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
