---
product: Kestrel Data Runner
version: v3
section: Configuration
---

# Backup schedule interval (Kestrel v3)

This page describes the backup schedule interval setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `KESTREL_BACKUP_SCHEDULE_INTERVAL`, as the environment variable. It takes a whole number of minutes. The default is **45 minutes**.

```
export KESTREL_BACKUP_SCHEDULE_INTERVAL=45
```

## Upgrading from version 2

`backup_schedule_interval`, the version 2 setting, is rejected. If it is still present the service refuses to start and logs `E1535: unknown setting backup_schedule_interval`. Remove it before upgrading.

## How it works

Internally, the service checks the backup schedule interval every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 45 minutes therefore means 'at least 45', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

Start from the default of 45 minutes and change it only with a reason you can write down. Raising the backup schedule interval trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 194 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_backup_schedule_interval_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 1. The highest accepted value is 194. A value outside that range is rejected and the previous value stays in force, with `E1535: KESTREL_BACKUP_SCHEDULE_INTERVAL out of range` in the log.

## Examples

| Value (minutes) | When to use it |
| --- | --- |
| 1 | small installations, or testing |
| 45 | the default; right for most installations |
| 90 | busy installations with spare capacity |
| 194 | the maximum; only with a reason written down |

## Interactions

The backup schedule interval is often changed together with the import file size limit (`KESTREL_IMPORT_FILE_SIZE_LIMIT`, default 74 days in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The backup schedule interval is often changed together with the two-factor grace period (`KESTREL_TWO_FACTOR_GRACE_PERIOD`, default 122 connections in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_BACKUP_SCHEDULE_INTERVAL` and given a new default of 45 minutes in release 3.1. Before that release, version 3 still used the version 2 name.

## Related

- Import file size limit: see the Import file size limit page for version 3.
- Two-factor grace period: see the Two-factor grace period page for version 3.
