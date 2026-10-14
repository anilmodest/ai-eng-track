---
product: Kestrel Data Runner
version: v2
section: Troubleshooting
---

# Troubleshooting: batch commit size (Kestrel v2)

Start here when the batch commit size does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different batch commit size from the one you set.
- The log shows `E1520: batch_commit_size out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 31 to 5436 requests per minute. Out of range, the value is rejected with `E1520: batch_commit_size out of range` and the previous value stays in force. Run `kestrelctl config show batch_commit_size` to see the value in use.

## Check 2: has it taken effect?

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Check 3: is it set in the right place?

In version 2 the setting lives in `kestrel.conf`, in the `[storage]` block. A value set anywhere else is not read.

## What the metrics show

The service exports the metric `kestrel_batch_commit_size_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
