---
product: Kestrel Data Runner
version: v3
section: Integrations
---

# Upload chunk size (Kestrel v3)

This page describes the upload chunk size setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `KESTREL_UPLOAD_CHUNK_SIZE`, in the admin console, under Settings > Configuration. It takes a whole number of seconds. The default is **97 seconds**.

The console shows the current value and the default side by side. The same value can be set from the command line with `kestrelctl config set KESTREL_UPLOAD_CHUNK_SIZE 97`.

## Upgrading from version 2

`upload_chunk_size`, the version 2 setting, is rejected. If it is still present the service refuses to start and logs `E1263: unknown setting upload_chunk_size`. Remove it before upgrading.

## How it works

Every request carries the upload chunk size that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 97 seconds. Large ones usually settle between the default and twice the default. Values near the minimum of 11 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_upload_chunk_size_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 11. The highest accepted value is 507. A value outside that range is rejected and the previous value stays in force, with `E1263: KESTREL_UPLOAD_CHUNK_SIZE out of range` in the log.

## Examples

| Value (seconds) | When to use it |
| --- | --- |
| 11 | small installations, or testing |
| 97 | the default; right for most installations |
| 194 | busy installations with spare capacity |
| 507 | the maximum; only with a reason written down |

## Interactions

The upload chunk size is often changed together with the connection pool size (`KESTREL_CONNECTION_POOL_SIZE`, default 33 minutes in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The upload chunk size is often changed together with the backup retention (`KESTREL_BACKUP_RETENTION`, default 518 requests per minute in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_UPLOAD_CHUNK_SIZE` and given a new default of 97 seconds in release 3.7. Before that release, version 3 still used the version 2 name.

## Related

- Connection pool size: see the Connection pool size page for version 3.
- Backup retention: see the Backup retention page for version 3.
