---
product: Kestrel Data Runner
version: v2
section: Configuration
---

# Retries (Kestrel v2)

When a connection attempt or a transfer fails, Kestrel retries it before marking the run as failed.

## Settings

`retry_count` in `kestrel.conf` sets how many retries follow the first attempt. The default is **3**. The interval between retries is fixed at **5 seconds** and cannot be configured.

```
[source]
retry_count = 3
```

## What is retried

Every failure is retried, including a rejected credential and a malformed request. A run that fails for a reason retrying cannot fix therefore takes `retry_count * 5` seconds longer than it needs to.

## Giving up

After the last retry the run is marked `failed` and the partial output is deleted.
