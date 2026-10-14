---
product: Kestrel Data Runner
version: v3
section: Configuration
---

# Import file size limit (Kestrel v3)

Kestrel Data Runner is a data runner that moves records between business systems. The import file size limit setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `KESTREL_IMPORT_FILE_SIZE_LIMIT`, as the environment variable. It takes a whole number of days. The default is **74 days**.

```
export KESTREL_IMPORT_FILE_SIZE_LIMIT=74
```

## Upgrading from version 2

`import_file_size_limit_day`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_IMPORT_FILE_SIZE_LIMIT` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

Every request carries the import file size limit that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 74 days. Large ones usually settle between the default and twice the default. Values near the minimum of 24 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_import_file_size_limit_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 24. The highest accepted value is 3495. A value outside that range is rejected and the previous value stays in force, with `E1478: KESTREL_IMPORT_FILE_SIZE_LIMIT out of range` in the log.

## Examples

| Value (days) | When to use it |
| --- | --- |
| 24 | small installations, or testing |
| 74 | the default; right for most installations |
| 148 | busy installations with spare capacity |
| 3495 | the maximum; only with a reason written down |

## Interactions

The import file size limit is often changed together with the backup schedule interval (`KESTREL_BACKUP_SCHEDULE_INTERVAL`, default 45 minutes in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The import file size limit is often changed together with the two-factor grace period (`KESTREL_TWO_FACTOR_GRACE_PERIOD`, default 122 connections in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_IMPORT_FILE_SIZE_LIMIT` and given a new default of 74 days in release 3.2. Before that release, version 3 still used the version 2 name.

## Related

- Backup schedule interval: see the Backup schedule interval page for version 3.
- Two-factor grace period: see the Two-factor grace period page for version 3.
