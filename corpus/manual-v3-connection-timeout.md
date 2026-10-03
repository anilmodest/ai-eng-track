---
product: Kestrel Data Runner
version: v3
section: Configuration
---

# Connection timeout (Kestrel v3)

Kestrel waits a fixed period for a source system to accept a connection before it gives up on that attempt and records a connection failure.

## Where the setting lives

The timeout is the environment variable `KESTREL_CONNECT_TIMEOUT`, in whole seconds. The default is **15 seconds**.

```
export KESTREL_CONNECT_TIMEOUT=15
```

`connection_timeout_seconds` in `kestrel.conf` is no longer used. If it is still present the runner **reads it, ignores it and starts normally**. Nothing is written to the log. A runner upgraded from version 2 without this change therefore runs on the version 3 default of 15 seconds, not on the value in the file, which is the most common cause of unexplained connection failures after an upgrade.

## When it takes effect

The value is read when the runner starts. Changing the variable has no effect on a running runner; restart the runner with `kestrelctl restart` for the new value to be used.

## Limits

The lowest accepted value is 1. The highest accepted value is 120. A value outside that range is rejected at startup and the runner refuses to start, with `E1104: KESTREL_CONNECT_TIMEOUT out of range` in the startup log.

## Related

A timeout is not a retry. See Retries for what Kestrel does after a connection attempt fails.
