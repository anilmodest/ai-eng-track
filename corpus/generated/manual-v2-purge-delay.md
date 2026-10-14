---
product: Kestrel Data Runner
version: v2
section: Integrations
---

# Purge delay (Kestrel v2)

Kestrel Data Runner is a data runner that moves records between business systems. The purge delay setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `purge_delay_ite`, in `kestrel.conf`, in the `[jobs]` block. It takes a whole number of items. The default is **2028 items**.

```
purge_delay_ite = 2028
```

## How it works

The purge delay is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 2028 items. Large ones usually settle between the default and twice the default. Values near the minimum of 125 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_purge_delay_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 125. The highest accepted value is 8599. A value outside that range is rejected and the previous value stays in force, with `E1623: purge_delay_ite out of range` in the log.

## Examples

| Value (items) | When to use it |
| --- | --- |
| 125 | small installations, or testing |
| 2028 | the default; right for most installations |
| 4056 | busy installations with spare capacity |
| 8599 | the maximum; only with a reason written down |

## Interactions

The purge delay is often changed together with the connection pool size (`connection_pool_size_min`, default 55 minutes in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The purge delay is often changed together with the backup retention (`backup_retention`, default 496 requests per minute in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `purge_delay_ite`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Connection pool size: see the Connection pool size page for version 2.
- Backup retention: see the Backup retention page for version 2.
