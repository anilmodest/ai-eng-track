---
product: Kestrel Data Runner
version: v2
section: Operations
---

# Log retention (Kestrel v2)

Kestrel keeps run logs on the runner's own disk.

## How long logs are kept

`log_retention_days` in `kestrel.conf` sets the number of days. The default is **14 days**. Logs older than that are deleted by a sweep that runs at startup and then once a day.

```
[runner]
log_retention_days = 14
```

## Where logs are written

`/var/log/kestrel/<run-id>.log`, one file per run, plain text.

## Limits

The highest accepted value is 90. Logs are not copied anywhere else; if the disk is lost, the logs are lost with it.
