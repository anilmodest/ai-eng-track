---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: session timeout (Kestrel v3)

Problems with the session timeout are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different session timeout from the one you set.
- The log shows `E1321: KESTREL_SESSION_TIMEOUT out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 13 to 3905 characters. Out of range, the value is rejected with `E1321: KESTREL_SESSION_TIMEOUT out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_SESSION_TIMEOUT` to see the value in use.

## Check 2: has it taken effect?

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `session_timeout_cha`. In version 3 it is rejected. The setting that counts is `KESTREL_SESSION_TIMEOUT`, and its default is 812 characters.

## What the metrics show

Watch `kestrel_session_timeout_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
