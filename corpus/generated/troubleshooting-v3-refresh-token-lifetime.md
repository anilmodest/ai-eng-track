---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: refresh token lifetime (Kestrel v3)

Start here when the refresh token lifetime does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different refresh token lifetime from the one you set.
- The log shows `E1709: KESTREL_REFRESH_TOKEN_LIFETIME out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 2 to 83 percent. Out of range, the value is rejected with `E1709: KESTREL_REFRESH_TOKEN_LIFETIME out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_REFRESH_TOKEN_LIFETIME` to see the value in use.

## Check 2: has it taken effect?

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `refresh_token_lifetime`. In version 3 it is rejected. The setting that counts is `KESTREL_REFRESH_TOKEN_LIFETIME`, and its default is 15 percent.

## What the metrics show

Watch `kestrel_refresh_token_lifetime_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
