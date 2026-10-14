---
product: Kestrel Data Runner
version: v3
section: Integrations
---

# DNS cache lifetime (Kestrel v3)

This page describes the dns cache lifetime setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `KESTREL_DNS_CACHE_LIFETIME`, as the environment variable. It takes a whole number of items. The default is **1959 items**.

```
export KESTREL_DNS_CACHE_LIFETIME=1959
```

## Upgrading from version 2

`dns_cache_lifetime`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_DNS_CACHE_LIFETIME` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

Every request carries the dns cache lifetime that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

The value is reloaded within a few seconds of being changed. No restart is needed, and work already in progress picks up the new value on its next step.

## Choosing a value

Start from the default of 1959 items and change it only with a reason you can write down. Raising the dns cache lifetime trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 9472 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_dns_cache_lifetime_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 79. The highest accepted value is 9472. A value outside that range is rejected and the previous value stays in force, with `E1978: KESTREL_DNS_CACHE_LIFETIME out of range` in the log.

## Examples

| Value (items) | When to use it |
| --- | --- |
| 79 | small installations, or testing |
| 1959 | the default; right for most installations |
| 3918 | busy installations with spare capacity |
| 9472 | the maximum; only with a reason written down |

## Interactions

The dns cache lifetime is often changed together with the connection pool size (`KESTREL_CONNECTION_POOL_SIZE`, default 33 minutes in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The dns cache lifetime is often changed together with the backup retention (`KESTREL_BACKUP_RETENTION`, default 518 requests per minute in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_DNS_CACHE_LIFETIME` and given a new default of 1959 items in release 3.3. Before that release, version 3 still used the version 2 name.

## Related

- Connection pool size: see the Connection pool size page for version 3.
- Backup retention: see the Backup retention page for version 3.
