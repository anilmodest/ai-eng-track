---
product: Kestrel Data Runner
version: v2
section: Troubleshooting
---

# Troubleshooting: webhook retry count (Kestrel v2)

Start here when the webhook retry count does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different webhook retry count from the one you set.
- The log shows `E1725: webhook_retry_count out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 1 to 97 percent. Out of range, the value is rejected with `E1725: webhook_retry_count out of range` and the previous value stays in force. Run `kestrelctl config show webhook_retry_count` to see the value in use.

## Check 2: has it taken effect?

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Check 3: is it set in the right place?

In version 2 the setting lives in `kestrel.conf`, in the `[jobs]` block. A value set anywhere else is not read.

## What the metrics show

The service exports the metric `kestrel_webhook_retry_count_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
