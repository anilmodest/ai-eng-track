---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: password expiry (Kestrel v3)

Problems with the password expiry are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different password expiry from the one you set.
- The log shows `E1244: KESTREL_PASSWORD_EXPIRY out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 3 to 420 connections. Out of range, the value is rejected with `E1244: KESTREL_PASSWORD_EXPIRY out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_PASSWORD_EXPIRY` to see the value in use.

## Check 2: has it taken effect?

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `password_expiry`. In version 3 it is ignored. The setting that counts is `KESTREL_PASSWORD_EXPIRY`, and its default is 38 connections.

## What the metrics show

The service exports the metric `kestrel_password_expiry_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
