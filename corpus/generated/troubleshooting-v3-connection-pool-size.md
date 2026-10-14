---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: connection pool size (Kestrel v3)

Start here when the connection pool size does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different connection pool size from the one you set.
- The log shows `E1194: KESTREL_CONNECTION_POOL_SIZE out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 1 to 230 minutes. Out of range, the value is rejected with `E1194: KESTREL_CONNECTION_POOL_SIZE out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_CONNECTION_POOL_SIZE` to see the value in use.

## Check 2: has it taken effect?

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `connection_pool_size_min`. In version 3 it is warned. The setting that counts is `KESTREL_CONNECTION_POOL_SIZE`, and its default is 33 minutes.

## What the metrics show

The service exports the metric `kestrel_connection_pool_size_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
