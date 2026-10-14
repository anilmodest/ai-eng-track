---
product: Kestrel Data Runner
version: v3
section: Configuration
---

# Field length limit (Kestrel v3)

Kestrel Data Runner is a data runner that moves records between business systems. The field length limit setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `KESTREL_FIELD_LENGTH_LIMIT`, in the admin console, under Settings > Security. It takes a whole number of percent. The default is **22 percent**.

The console shows the current value and the default side by side. The same value can be set from the command line with `kestrelctl config set KESTREL_FIELD_LENGTH_LIMIT 22`.

## Upgrading from version 2

`field_length_limit`, the version 2 setting, is rejected. If it is still present the service refuses to start and logs `E1807: unknown setting field_length_limit`. Remove it before upgrading.

## How it works

Internally, the service checks the field length limit every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 22 percent therefore means 'at least 22', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 22 percent. Large ones usually settle between the default and twice the default. Values near the minimum of 1 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_field_length_limit_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 1. The highest accepted value is 79. A value outside that range is rejected and the previous value stays in force, with `E1807: KESTREL_FIELD_LENGTH_LIMIT out of range` in the log.

## Examples

| Value (percent) | When to use it |
| --- | --- |
| 1 | small installations, or testing |
| 22 | the default; right for most installations |
| 44 | busy installations with spare capacity |
| 79 | the maximum; only with a reason written down |

## Interactions

The field length limit is often changed together with the import file size limit (`KESTREL_IMPORT_FILE_SIZE_LIMIT`, default 74 days in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The field length limit is often changed together with the backup schedule interval (`KESTREL_BACKUP_SCHEDULE_INTERVAL`, default 45 minutes in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_FIELD_LENGTH_LIMIT` and given a new default of 22 percent in release 3.6. Before that release, version 3 still used the version 2 name.

## Related

- Import file size limit: see the Import file size limit page for version 3.
- Backup schedule interval: see the Backup schedule interval page for version 3.
