---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: health check interval (Kestrel v3)

Problems with the health check interval are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different health check interval from the one you set.
- The log shows `E1773: KESTREL_HEALTH_CHECK_INTERVAL out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 66 to 2915 days. Out of range, the value is rejected with `E1773: KESTREL_HEALTH_CHECK_INTERVAL out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_HEALTH_CHECK_INTERVAL` to see the value in use.

## Check 2: has it taken effect?

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `health_check_interval`. In version 3 it is ignored. The setting that counts is `KESTREL_HEALTH_CHECK_INTERVAL`, and its default is 141 days.

## What the metrics show

Watch `kestrel_health_check_interval_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
