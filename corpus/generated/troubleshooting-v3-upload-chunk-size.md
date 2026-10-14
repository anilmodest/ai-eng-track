---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: upload chunk size (Kestrel v3)

Start here when the upload chunk size does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different upload chunk size from the one you set.
- The log shows `E1263: KESTREL_UPLOAD_CHUNK_SIZE out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 11 to 507 seconds. Out of range, the value is rejected with `E1263: KESTREL_UPLOAD_CHUNK_SIZE out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_UPLOAD_CHUNK_SIZE` to see the value in use.

## Check 2: has it taken effect?

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `upload_chunk_size`. In version 3 it is rejected. The setting that counts is `KESTREL_UPLOAD_CHUNK_SIZE`, and its default is 97 seconds.

## What the metrics show

Watch `kestrel_upload_chunk_size_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
