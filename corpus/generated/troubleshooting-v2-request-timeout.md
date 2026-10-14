---
product: Kestrel Data Runner
version: v2
section: Troubleshooting
---

# Troubleshooting: request timeout (Kestrel v2)

Start here when the request timeout does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different request timeout from the one you set.
- The log shows `E1164: request_timeout out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 1 to 151 hours. Out of range, the value is rejected with `E1164: request_timeout out of range` and the previous value stays in force. Run `kestrelctl config show request_timeout` to see the value in use.

## Check 2: has it taken effect?

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Check 3: is it set in the right place?

In version 2 the setting lives in `kestrel.conf`, in the `[security]` block. A value set anywhere else is not read.

## What the metrics show

The service exports the metric `kestrel_request_timeout_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
