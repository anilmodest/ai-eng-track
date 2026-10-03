---
product: Kestrel Data Runner
version: v3
section: Operations
---

# Log retention (Kestrel v3)

Kestrel keeps run logs on the runner's own disk and copies them to object storage.

## How long logs are kept

`KESTREL_LOG_RETENTION_DAYS` sets the number of days kept on disk. The default is **7 days**. Logs older than that are deleted by a sweep that runs at startup and then once an hour.

```
export KESTREL_LOG_RETENTION_DAYS=7
```

## Where logs are written

`/var/log/kestrel/<run-id>.log` as before, and each closed log is also uploaded to the export bucket under `logs/<date>/<run-id>.log.gz`, where it is kept for **365 days** regardless of the on-disk setting.

## Limits

The highest accepted value for the on-disk setting is 30. A value above 30 is rejected at startup with `E2210`.
