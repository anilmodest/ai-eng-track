---
product: Kestrel Data Runner
version: v2
section: Integrations
---

# Scheduler worker count (Kestrel v2)

Kestrel Data Runner is a data runner that moves records between business systems. The scheduler worker count setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `scheduler_worker_count`, in `kestrel.conf`, in the `[network]` block. It takes a whole number of minutes. The default is **18 minutes**.

```
scheduler_worker_count = 18
```

## How it works

Internally, the service checks the scheduler worker count every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 18 minutes therefore means 'at least 18', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 18 minutes. Large ones usually settle between the default and twice the default. Values near the minimum of 1 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_scheduler_worker_count_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 1. The highest accepted value is 209. A value outside that range is rejected and the previous value stays in force, with `E1929: scheduler_worker_count out of range` in the log.

## Examples

| Value (minutes) | When to use it |
| --- | --- |
| 1 | small installations, or testing |
| 18 | the default; right for most installations |
| 36 | busy installations with spare capacity |
| 209 | the maximum; only with a reason written down |

## Interactions

The scheduler worker count is often changed together with the connection pool size (`connection_pool_size_min`, default 55 minutes in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The scheduler worker count is often changed together with the backup retention (`backup_retention`, default 496 requests per minute in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `scheduler_worker_count`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Connection pool size: see the Connection pool size page for version 2.
- Backup retention: see the Backup retention page for version 2.
