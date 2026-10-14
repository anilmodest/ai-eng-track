---
product: Kestrel Data Runner
version: v3
section: Configuration
---

# Archive threshold (Kestrel v3)

This page describes the archive threshold setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `KESTREL_ARCHIVE_THRESHOLD`, as the environment variable. It takes a whole number of minutes. The default is **21 minutes**.

```
export KESTREL_ARCHIVE_THRESHOLD=21
```

## Upgrading from version 2

`archive_threshold`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_ARCHIVE_THRESHOLD` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

Every request carries the archive threshold that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 21 minutes. Large ones usually settle between the default and twice the default. Values near the minimum of 5 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_archive_threshold_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 5. The highest accepted value is 235. A value outside that range is rejected and the previous value stays in force, with `E1107: KESTREL_ARCHIVE_THRESHOLD out of range` in the log.

## Examples

| Value (minutes) | When to use it |
| --- | --- |
| 5 | small installations, or testing |
| 21 | the default; right for most installations |
| 42 | busy installations with spare capacity |
| 235 | the maximum; only with a reason written down |

## Interactions

The archive threshold is often changed together with the import file size limit (`KESTREL_IMPORT_FILE_SIZE_LIMIT`, default 74 days in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The archive threshold is often changed together with the backup schedule interval (`KESTREL_BACKUP_SCHEDULE_INTERVAL`, default 45 minutes in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_ARCHIVE_THRESHOLD` and given a new default of 21 minutes in release 3.6. Before that release, version 3 still used the version 2 name.

## Related

- Import file size limit: see the Import file size limit page for version 3.
- Backup schedule interval: see the Backup schedule interval page for version 3.
