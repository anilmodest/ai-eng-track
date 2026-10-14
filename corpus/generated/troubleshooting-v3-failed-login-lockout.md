---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: failed login lockout (Kestrel v3)

Start here when the failed login lockout does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different failed login lockout from the one you set.
- The log shows `E1618: KESTREL_FAILED_LOGIN_LOCKOUT out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 6 to 485 connections. Out of range, the value is rejected with `E1618: KESTREL_FAILED_LOGIN_LOCKOUT out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_FAILED_LOGIN_LOCKOUT` to see the value in use.

## Check 2: has it taken effect?

The value is reloaded within a few seconds of being changed. No restart is needed, and work already in progress picks up the new value on its next step.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `failed_login_lockout`. In version 3 it is rejected. The setting that counts is `KESTREL_FAILED_LOGIN_LOCKOUT`, and its default is 127 connections.

## What the metrics show

Watch `kestrel_failed_login_lockout_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
