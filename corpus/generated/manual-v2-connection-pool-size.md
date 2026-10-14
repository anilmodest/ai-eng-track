---
product: Kestrel Data Runner
version: v2
section: Integrations
---

# Connection pool size (Kestrel v2)

This page describes the connection pool size setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `connection_pool_size_min`, in `kestrel.conf`, in the `[network]` block. It takes a whole number of minutes. The default is **55 minutes**.

```
connection_pool_size_min = 55
```

## How it works

The connection pool size is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 55 minutes. Large ones usually settle between the default and twice the default. Values near the minimum of 1 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_connection_pool_size_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 1. The highest accepted value is 193. A value outside that range is rejected and the previous value stays in force, with `E1194: connection_pool_size_min out of range` in the log.

## Examples

| Value (minutes) | When to use it |
| --- | --- |
| 1 | small installations, or testing |
| 55 | the default; right for most installations |
| 110 | busy installations with spare capacity |
| 193 | the maximum; only with a reason written down |

## Interactions

The connection pool size is often changed together with the backup retention (`backup_retention`, default 496 requests per minute in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The connection pool size is often changed together with the password expiry (`password_expiry`, default 114 connections in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `connection_pool_size_min`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Backup retention: see the Backup retention page for version 2.
- Password expiry: see the Password expiry page for version 2.
