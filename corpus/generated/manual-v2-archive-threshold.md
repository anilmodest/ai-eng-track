---
product: Kestrel Data Runner
version: v2
section: Configuration
---

# Archive threshold (Kestrel v2)

In Kestrel Data Runner, the archive threshold is a single value measured in minutes. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `archive_threshold`, in `kestrel.conf`, in the `[jobs]` block. It takes a whole number of minutes. The default is **32 minutes**.

```
archive_threshold = 32
```

## How it works

Internally, the service checks the archive threshold every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 32 minutes therefore means 'at least 32', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 32 minutes. Large ones usually settle between the default and twice the default. Values near the minimum of 5 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_archive_threshold_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 5. The highest accepted value is 234. A value outside that range is rejected and the previous value stays in force, with `E1107: archive_threshold out of range` in the log.

## Examples

| Value (minutes) | When to use it |
| --- | --- |
| 5 | small installations, or testing |
| 32 | the default; right for most installations |
| 64 | busy installations with spare capacity |
| 234 | the maximum; only with a reason written down |

## Interactions

The archive threshold is often changed together with the import file size limit (`import_file_size_limit_day`, default 66 days in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The archive threshold is often changed together with the backup schedule interval (`backup_schedule_interval`, default 66 minutes in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `archive_threshold`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Import file size limit: see the Import file size limit page for version 2.
- Backup schedule interval: see the Backup schedule interval page for version 2.
