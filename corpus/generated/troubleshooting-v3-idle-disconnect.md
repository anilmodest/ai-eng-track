---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: idle disconnect (Kestrel v3)

Start here when the idle disconnect does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different idle disconnect from the one you set.
- The log shows `E1948: KESTREL_IDLE_DISCONNECT out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 164 to 9796 items. Out of range, the value is rejected with `E1948: KESTREL_IDLE_DISCONNECT out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_IDLE_DISCONNECT` to see the value in use.

## Check 2: has it taken effect?

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `idle_disconnect`. In version 3 it is warned. The setting that counts is `KESTREL_IDLE_DISCONNECT`, and its default is 2804 items.

## What the metrics show

Watch `kestrel_idle_disconnect_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
