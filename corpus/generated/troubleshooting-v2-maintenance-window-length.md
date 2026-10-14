---
product: Kestrel Data Runner
version: v2
section: Troubleshooting
---

# Troubleshooting: maintenance window length (Kestrel v2)

Start here when the maintenance window length does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different maintenance window length from the one you set.
- The log shows `E1129: maintenance_window_length_con out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 6 to 393 connections. Out of range, the value is rejected with `E1129: maintenance_window_length_con out of range` and the previous value stays in force. Run `kestrelctl config show maintenance_window_length_con` to see the value in use.

## Check 2: has it taken effect?

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Check 3: is it set in the right place?

In version 2 the setting lives in `kestrel.conf`, in the `[network]` block. A value set anywhere else is not read.

## What the metrics show

Watch `kestrel_maintenance_window_length_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
