---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: report page size (Kestrel v3)

Problems with the report page size are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different report page size from the one you set.
- The log shows `E1717: KESTREL_REPORT_PAGE_SIZE out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 10 to 499 connections. Out of range, the value is rejected with `E1717: KESTREL_REPORT_PAGE_SIZE out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_REPORT_PAGE_SIZE` to see the value in use.

## Check 2: has it taken effect?

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `report_page_size`. In version 3 it is rejected. The setting that counts is `KESTREL_REPORT_PAGE_SIZE`, and its default is 157 connections.

## What the metrics show

Watch `kestrel_report_page_size_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
