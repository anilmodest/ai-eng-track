---
product: Kestrel Data Runner
version: v2
section: Troubleshooting
---

# Troubleshooting: upload chunk size (Kestrel v2)

Problems with the upload chunk size are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different upload chunk size from the one you set.
- The log shows `E1263: upload_chunk_size out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 8 to 586 seconds. Out of range, the value is rejected with `E1263: upload_chunk_size out of range` and the previous value stays in force. Run `kestrelctl config show upload_chunk_size` to see the value in use.

## Check 2: has it taken effect?

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Check 3: is it set in the right place?

In version 2 the setting lives in `kestrel.conf`, in the `[jobs]` block. A value set anywhere else is not read.

## What the metrics show

The service exports the metric `kestrel_upload_chunk_size_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
