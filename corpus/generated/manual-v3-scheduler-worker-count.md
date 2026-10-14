---
product: Kestrel Data Runner
version: v3
section: Integrations
---

# Scheduler worker count (Kestrel v3)

Kestrel Data Runner is a data runner that moves records between business systems. The scheduler worker count setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `KESTREL_SCHEDULER_WORKER_COUNT`, in the admin console, under Settings > Integrations. It takes a whole number of minutes. The default is **28 minutes**.

The console shows the current value and the default side by side. The same value can be set from the command line with `kestrelctl config set KESTREL_SCHEDULER_WORKER_COUNT 28`.

## Upgrading from version 2

`scheduler_worker_count`, the version 2 setting, is rejected. If it is still present the service refuses to start and logs `E1929: unknown setting scheduler_worker_count`. Remove it before upgrading.

## How it works

The scheduler worker count is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

Start from the default of 28 minutes and change it only with a reason you can write down. Raising the scheduler worker count trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 238 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_scheduler_worker_count_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 2. The highest accepted value is 238. A value outside that range is rejected and the previous value stays in force, with `E1929: KESTREL_SCHEDULER_WORKER_COUNT out of range` in the log.

## Examples

| Value (minutes) | When to use it |
| --- | --- |
| 2 | small installations, or testing |
| 28 | the default; right for most installations |
| 56 | busy installations with spare capacity |
| 238 | the maximum; only with a reason written down |

## Interactions

The scheduler worker count is often changed together with the connection pool size (`KESTREL_CONNECTION_POOL_SIZE`, default 33 minutes in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The scheduler worker count is often changed together with the backup retention (`KESTREL_BACKUP_RETENTION`, default 518 requests per minute in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_SCHEDULER_WORKER_COUNT` and given a new default of 28 minutes in release 3.6. Before that release, version 3 still used the version 2 name.

## Related

- Connection pool size: see the Connection pool size page for version 3.
- Backup retention: see the Backup retention page for version 3.
