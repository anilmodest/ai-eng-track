---
product: Kestrel Data Runner
version: v2
section: Integrations
---

# DNS cache lifetime (Kestrel v2)

Kestrel Data Runner is a data runner that moves records between business systems. The dns cache lifetime setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `dns_cache_lifetime`, in `kestrel.conf`, in the `[jobs]` block. It takes a whole number of items. The default is **2822 items**.

```
dns_cache_lifetime = 2822
```

## How it works

Every request carries the dns cache lifetime that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

Start from the default of 2822 items and change it only with a reason you can write down. Raising the dns cache lifetime trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 8583 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_dns_cache_lifetime_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 88. The highest accepted value is 8583. A value outside that range is rejected and the previous value stays in force, with `E1978: dns_cache_lifetime out of range` in the log.

## Examples

| Value (items) | When to use it |
| --- | --- |
| 88 | small installations, or testing |
| 2822 | the default; right for most installations |
| 5644 | busy installations with spare capacity |
| 8583 | the maximum; only with a reason written down |

## Interactions

The dns cache lifetime is often changed together with the connection pool size (`connection_pool_size_min`, default 55 minutes in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The dns cache lifetime is often changed together with the backup retention (`backup_retention`, default 496 requests per minute in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `dns_cache_lifetime`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Connection pool size: see the Connection pool size page for version 2.
- Backup retention: see the Backup retention page for version 2.
