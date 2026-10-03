---
product: Kestrel Data Runner
version: v3
section: Configuration
---

# Retries (Kestrel v3)

When a connection attempt or a transfer fails, Kestrel retries it before marking the run as failed.

## Settings

`KESTREL_RETRY_MAX` sets how many retries follow the first attempt. The default is **6**. `KESTREL_RETRY_POLICY` takes `exponential` or `fixed` and defaults to `exponential`, starting at **2 seconds** and doubling, capped at 60 seconds.

```
export KESTREL_RETRY_MAX=6
export KESTREL_RETRY_POLICY=exponential
```

`retry_count` in `kestrel.conf` is no longer used and is ignored silently.

## What is retried

Only failures that retrying can fix: timeouts, connection resets, and responses with status 429 or 5xx. A rejected credential or a malformed request fails the run immediately, without retrying.

## Giving up

After the last retry the run is marked `failed` and the partial output is **kept** under `runs/<run-id>/partial/`, so a long transfer can be resumed with `kestrelctl resume <run-id>`.
