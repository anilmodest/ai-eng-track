---
product: Kestrel Data Runner
version: v2
section: Troubleshooting
---

# Troubleshooting: two-factor grace period (Kestrel v2)

Start here when the two-factor grace period does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different two-factor grace period from the one you set.
- The log shows `E1693: two_factor_grace_period out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 1 to 404 connections. Out of range, the value is rejected with `E1693: two_factor_grace_period out of range` and the previous value stays in force. Run `kestrelctl config show two_factor_grace_period` to see the value in use.

## Check 2: has it taken effect?

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Check 3: is it set in the right place?

In version 2 the setting lives in `kestrel.conf`, in the `[source]` block. A value set anywhere else is not read.

## What the metrics show

The service exports the metric `kestrel_two_factor_grace_period_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
