---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: two-factor grace period (Kestrel v3)

Problems with the two-factor grace period are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different two-factor grace period from the one you set.
- The log shows `E1693: KESTREL_TWO_FACTOR_GRACE_PERIOD out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 8 to 466 connections. Out of range, the value is rejected with `E1693: KESTREL_TWO_FACTOR_GRACE_PERIOD out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_TWO_FACTOR_GRACE_PERIOD` to see the value in use.

## Check 2: has it taken effect?

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `two_factor_grace_period`. In version 3 it is warned. The setting that counts is `KESTREL_TWO_FACTOR_GRACE_PERIOD`, and its default is 122 connections.

## What the metrics show

Watch `kestrel_two_factor_grace_period_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
