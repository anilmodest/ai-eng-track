---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: maintenance window length (Kestrel v3)

Start here when the maintenance window length does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different maintenance window length from the one you set.
- The log shows `E1129: KESTREL_MAINTENANCE_WINDOW_LENGTH out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 1 to 482 connections. Out of range, the value is rejected with `E1129: KESTREL_MAINTENANCE_WINDOW_LENGTH out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_MAINTENANCE_WINDOW_LENGTH` to see the value in use.

## Check 2: has it taken effect?

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `maintenance_window_length_con`. In version 3 it is rejected. The setting that counts is `KESTREL_MAINTENANCE_WINDOW_LENGTH`, and its default is 87 connections.

## What the metrics show

Watch `kestrel_maintenance_window_length_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
