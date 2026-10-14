---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: source poll interval (Kestrel v3)

Start here when the source poll interval does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different source poll interval from the one you set.
- The log shows `E1260: KESTREL_SOURCE_POLL_INTERVAL out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 5 to 193 minutes. Out of range, the value is rejected with `E1260: KESTREL_SOURCE_POLL_INTERVAL out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_SOURCE_POLL_INTERVAL` to see the value in use.

## Check 2: has it taken effect?

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `source_poll_interval`. In version 3 it is ignored. The setting that counts is `KESTREL_SOURCE_POLL_INTERVAL`, and its default is 29 minutes.

## What the metrics show

Watch `kestrel_source_poll_interval_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
