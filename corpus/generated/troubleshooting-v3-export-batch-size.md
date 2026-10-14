---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: export batch size (Kestrel v3)

Problems with the export batch size are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different export batch size from the one you set.
- The log shows `E1622: KESTREL_EXPORT_BATCH_SIZE out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 7 to 571 seconds. Out of range, the value is rejected with `E1622: KESTREL_EXPORT_BATCH_SIZE out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_EXPORT_BATCH_SIZE` to see the value in use.

## Check 2: has it taken effect?

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `export_batch_size_sec`. In version 3 it is rejected. The setting that counts is `KESTREL_EXPORT_BATCH_SIZE`, and its default is 57 seconds.

## What the metrics show

Watch `kestrel_export_batch_size_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
