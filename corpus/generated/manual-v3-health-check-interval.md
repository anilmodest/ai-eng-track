---
product: Kestrel Data Runner
version: v3
section: Configuration
---

# Health check interval (Kestrel v3)

In Kestrel Data Runner, the health check interval is a single value measured in days. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `KESTREL_HEALTH_CHECK_INTERVAL`, in the admin console, under Settings > Operations. It takes a whole number of days. The default is **141 days**.

The console shows the current value and the default side by side. The same value can be set from the command line with `kestrelctl config set KESTREL_HEALTH_CHECK_INTERVAL 141`.

## Upgrading from version 2

`health_check_interval`, the version 2 setting, is no longer used. If it is still present the service **reads it, ignores it and starts normally**. Nothing is written to the log. An installation upgraded from version 2 without this change therefore runs on the version 3 default of 141 days, not on the value in the old file.

## How it works

Internally, the service checks the health check interval every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 141 days therefore means 'at least 141', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 141 days. Large ones usually settle between the default and twice the default. Values near the minimum of 66 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_health_check_interval_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 66. The highest accepted value is 2915. A value outside that range is rejected and the previous value stays in force, with `E1773: KESTREL_HEALTH_CHECK_INTERVAL out of range` in the log.

## Examples

| Value (days) | When to use it |
| --- | --- |
| 66 | small installations, or testing |
| 141 | the default; right for most installations |
| 282 | busy installations with spare capacity |
| 2915 | the maximum; only with a reason written down |

## Interactions

The health check interval is often changed together with the import file size limit (`KESTREL_IMPORT_FILE_SIZE_LIMIT`, default 74 days in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The health check interval is often changed together with the backup schedule interval (`KESTREL_BACKUP_SCHEDULE_INTERVAL`, default 45 minutes in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_HEALTH_CHECK_INTERVAL` and given a new default of 141 days in release 3.0. Before that release, version 3 still used the version 2 name.

## Related

- Import file size limit: see the Import file size limit page for version 3.
- Backup schedule interval: see the Backup schedule interval page for version 3.
