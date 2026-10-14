---
product: Kestrel Data Runner
version: v2
section: Configuration
---

# Two-factor grace period (Kestrel v2)

Kestrel Data Runner is a data runner that moves records between business systems. The two-factor grace period setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `two_factor_grace_period`, in `kestrel.conf`, in the `[source]` block. It takes a whole number of connections. The default is **68 connections**.

```
two_factor_grace_period = 68
```

## How it works

Internally, the service checks the two-factor grace period every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 68 connections therefore means 'at least 68', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 68 connections. Large ones usually settle between the default and twice the default. Values near the minimum of 1 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_two_factor_grace_period_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 1. The highest accepted value is 404. A value outside that range is rejected and the previous value stays in force, with `E1693: two_factor_grace_period out of range` in the log.

## Examples

| Value (connections) | When to use it |
| --- | --- |
| 1 | small installations, or testing |
| 68 | the default; right for most installations |
| 136 | busy installations with spare capacity |
| 404 | the maximum; only with a reason written down |

## Interactions

The two-factor grace period is often changed together with the import file size limit (`import_file_size_limit_day`, default 66 days in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The two-factor grace period is often changed together with the backup schedule interval (`backup_schedule_interval`, default 66 minutes in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `two_factor_grace_period`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Import file size limit: see the Import file size limit page for version 2.
- Backup schedule interval: see the Backup schedule interval page for version 2.
