---
product: Kestrel Data Runner
version: v2
section: Troubleshooting
---

# Troubleshooting: archive threshold (Kestrel v2)

Start here when the archive threshold does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different archive threshold from the one you set.
- The log shows `E1107: archive_threshold out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 5 to 234 minutes. Out of range, the value is rejected with `E1107: archive_threshold out of range` and the previous value stays in force. Run `kestrelctl config show archive_threshold` to see the value in use.

## Check 2: has it taken effect?

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Check 3: is it set in the right place?

In version 2 the setting lives in `kestrel.conf`, in the `[jobs]` block. A value set anywhere else is not read.

## What the metrics show

Watch `kestrel_archive_threshold_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
