---
product: Kestrel Data Runner
version: v2
section: Troubleshooting
---

# Troubleshooting: password minimum length (Kestrel v2)

Start here when the password minimum length does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different password minimum length from the one you set.
- The log shows `E1362: password_minimum_length_req out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 96 to 5905 requests per minute. Out of range, the value is rejected with `E1362: password_minimum_length_req out of range` and the previous value stays in force. Run `kestrelctl config show password_minimum_length_req` to see the value in use.

## Check 2: has it taken effect?

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Check 3: is it set in the right place?

In version 2 the setting lives in `kestrel.conf`, in the `[server]` block. A value set anywhere else is not read.

## What the metrics show

Watch `kestrel_password_minimum_length_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
