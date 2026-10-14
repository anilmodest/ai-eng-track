---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: import file size limit (Kestrel v3)

Problems with the import file size limit are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different import file size limit from the one you set.
- The log shows `E1478: KESTREL_IMPORT_FILE_SIZE_LIMIT out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 24 to 3495 days. Out of range, the value is rejected with `E1478: KESTREL_IMPORT_FILE_SIZE_LIMIT out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_IMPORT_FILE_SIZE_LIMIT` to see the value in use.

## Check 2: has it taken effect?

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `import_file_size_limit_day`. In version 3 it is warned. The setting that counts is `KESTREL_IMPORT_FILE_SIZE_LIMIT`, and its default is 74 days.

## What the metrics show

Watch `kestrel_import_file_size_limit_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
