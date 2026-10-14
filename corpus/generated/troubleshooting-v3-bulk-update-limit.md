---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: bulk update limit (Kestrel v3)

Start here when the bulk update limit does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different bulk update limit from the one you set.
- The log shows `E1816: KESTREL_BULK_UPDATE_LIMIT out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 4 to 128 hours. Out of range, the value is rejected with `E1816: KESTREL_BULK_UPDATE_LIMIT out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_BULK_UPDATE_LIMIT` to see the value in use.

## Check 2: has it taken effect?

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `bulk_update_limit`. In version 3 it is rejected. The setting that counts is `KESTREL_BULK_UPDATE_LIMIT`, and its default is 9 hours.

## What the metrics show

Watch `kestrel_bulk_update_limit_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
