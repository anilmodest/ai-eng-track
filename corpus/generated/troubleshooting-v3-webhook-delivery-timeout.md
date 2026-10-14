---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: webhook delivery timeout (Kestrel v3)

Start here when the webhook delivery timeout does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different webhook delivery timeout from the one you set.
- The log shows `E1220: KESTREL_WEBHOOK_DELIVERY_TIMEOUT out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 2 to 94 percent. Out of range, the value is rejected with `E1220: KESTREL_WEBHOOK_DELIVERY_TIMEOUT out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_WEBHOOK_DELIVERY_TIMEOUT` to see the value in use.

## Check 2: has it taken effect?

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `webhook_delivery_timeout_per`. In version 3 it is warned. The setting that counts is `KESTREL_WEBHOOK_DELIVERY_TIMEOUT`, and its default is 3 percent.

## What the metrics show

The service exports the metric `kestrel_webhook_delivery_timeout_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
