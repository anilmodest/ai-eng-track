---
product: Kestrel Data Runner
version: v2
section: Troubleshooting
---

# Troubleshooting: password expiry (Kestrel v2)

Start here when the password expiry does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different password expiry from the one you set.
- The log shows `E1244: password_expiry out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 2 to 450 connections. Out of range, the value is rejected with `E1244: password_expiry out of range` and the previous value stays in force. Run `kestrelctl config show password_expiry` to see the value in use.

## Check 2: has it taken effect?

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Check 3: is it set in the right place?

In version 2 the setting lives in `kestrel.conf`, in the `[source]` block. A value set anywhere else is not read.

## What the metrics show

Watch `kestrel_password_expiry_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
