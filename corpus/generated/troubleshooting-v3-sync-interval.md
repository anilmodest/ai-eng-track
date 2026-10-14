---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: sync interval (Kestrel v3)

Start here when the sync interval does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different sync interval from the one you set.
- The log shows `E1584: KESTREL_SYNC_INTERVAL out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 31 to 1577 megabytes. Out of range, the value is rejected with `E1584: KESTREL_SYNC_INTERVAL out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_SYNC_INTERVAL` to see the value in use.

## Check 2: has it taken effect?

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `sync_interval`. In version 3 it is warned. The setting that counts is `KESTREL_SYNC_INTERVAL`, and its default is 383 megabytes.

## What the metrics show

Watch `kestrel_sync_interval_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
