---
product: Kestrel Data Runner
version: v3
section: Integrations
---

# Connection pool size (Kestrel v3)

In Kestrel Data Runner, the connection pool size is a single value measured in minutes. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `KESTREL_CONNECTION_POOL_SIZE`, in the admin console, under Settings > Data. It takes a whole number of minutes. The default is **33 minutes**.

The console shows the current value and the default side by side. The same value can be set from the command line with `kestrelctl config set KESTREL_CONNECTION_POOL_SIZE 33`.

## Upgrading from version 2

`connection_pool_size_min`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_CONNECTION_POOL_SIZE` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

Every request carries the connection pool size that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Choosing a value

Start from the default of 33 minutes and change it only with a reason you can write down. Raising the connection pool size trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 230 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_connection_pool_size_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 1. The highest accepted value is 230. A value outside that range is rejected and the previous value stays in force, with `E1194: KESTREL_CONNECTION_POOL_SIZE out of range` in the log.

## Examples

| Value (minutes) | When to use it |
| --- | --- |
| 1 | small installations, or testing |
| 33 | the default; right for most installations |
| 66 | busy installations with spare capacity |
| 230 | the maximum; only with a reason written down |

## Interactions

The connection pool size is often changed together with the backup retention (`KESTREL_BACKUP_RETENTION`, default 518 requests per minute in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The connection pool size is often changed together with the password expiry (`KESTREL_PASSWORD_EXPIRY`, default 38 connections in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_CONNECTION_POOL_SIZE` and given a new default of 33 minutes in release 3.5. Before that release, version 3 still used the version 2 name.

## Related

- Backup retention: see the Backup retention page for version 3.
- Password expiry: see the Password expiry page for version 3.
