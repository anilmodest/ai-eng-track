---
product: Kestrel Data Runner
version: v2
section: Configuration
---

# Connection timeout (Kestrel v2)

Kestrel waits a fixed period for a source system to accept a connection before it gives up on that attempt and records a connection failure.

## Where the setting lives

The timeout is `connection_timeout_seconds` in `kestrel.conf`, in the `[source]` block. It takes a whole number of seconds. The default is **30 seconds**.

```
[source]
connection_timeout_seconds = 30
```

## When it takes effect

The value is read when the runner starts. Changing it in `kestrel.conf` has no effect on a running runner; restart the runner with `kestrelctl restart` for the new value to be used.

## Limits

The lowest accepted value is 5. The highest accepted value is 300. A value outside that range is rejected at startup and the runner refuses to start, with `E1104: connection_timeout_seconds out of range` in the startup log.

## Related

A timeout is not a retry. See Retries for what Kestrel does after a connection attempt fails.
