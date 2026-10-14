---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: purge delay (Kestrel v3)

Problems with the purge delay are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different purge delay from the one you set.
- The log shows `E1623: KESTREL_PURGE_DELAY out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 128 to 8289 items. Out of range, the value is rejected with `E1623: KESTREL_PURGE_DELAY out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_PURGE_DELAY` to see the value in use.

## Check 2: has it taken effect?

The value is reloaded within a few seconds of being changed. No restart is needed, and work already in progress picks up the new value on its next step.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `purge_delay_ite`. In version 3 it is rejected. The setting that counts is `KESTREL_PURGE_DELAY`, and its default is 2444 items.

## What the metrics show

Watch `kestrel_purge_delay_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
