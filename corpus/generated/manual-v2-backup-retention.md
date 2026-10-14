---
product: Kestrel Data Runner
version: v2
section: Integrations
---

# Backup retention (Kestrel v2)

Kestrel Data Runner is a data runner that moves records between business systems. The backup retention setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `backup_retention`, in `kestrel.conf`, in the `[jobs]` block. It takes a whole number of requests per minute. The default is **496 requests per minute**.

```
backup_retention = 496
```

## How it works

Every request carries the backup retention that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 496 requests per minute. Large ones usually settle between the default and twice the default. Values near the minimum of 26 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_backup_retention_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 26. The highest accepted value is 5504. A value outside that range is rejected and the previous value stays in force, with `E1956: backup_retention out of range` in the log.

## Examples

| Value (requests per minute) | When to use it |
| --- | --- |
| 26 | small installations, or testing |
| 496 | the default; right for most installations |
| 992 | busy installations with spare capacity |
| 5504 | the maximum; only with a reason written down |

## Interactions

The backup retention is often changed together with the connection pool size (`connection_pool_size_min`, default 55 minutes in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The backup retention is often changed together with the password expiry (`password_expiry`, default 114 connections in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `backup_retention`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Connection pool size: see the Connection pool size page for version 2.
- Password expiry: see the Password expiry page for version 2.
