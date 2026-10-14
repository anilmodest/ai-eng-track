---
product: Kestrel Data Runner
version: v3
section: Configuration
---

# Two-factor grace period (Kestrel v3)

In Kestrel Data Runner, the two-factor grace period is a single value measured in connections. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `KESTREL_TWO_FACTOR_GRACE_PERIOD`, as the environment variable. It takes a whole number of connections. The default is **122 connections**.

```
export KESTREL_TWO_FACTOR_GRACE_PERIOD=122
```

## Upgrading from version 2

`two_factor_grace_period`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_TWO_FACTOR_GRACE_PERIOD` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

The two-factor grace period is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 122 connections. Large ones usually settle between the default and twice the default. Values near the minimum of 8 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_two_factor_grace_period_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 8. The highest accepted value is 466. A value outside that range is rejected and the previous value stays in force, with `E1693: KESTREL_TWO_FACTOR_GRACE_PERIOD out of range` in the log.

## Examples

| Value (connections) | When to use it |
| --- | --- |
| 8 | small installations, or testing |
| 122 | the default; right for most installations |
| 244 | busy installations with spare capacity |
| 466 | the maximum; only with a reason written down |

## Interactions

The two-factor grace period is often changed together with the import file size limit (`KESTREL_IMPORT_FILE_SIZE_LIMIT`, default 74 days in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The two-factor grace period is often changed together with the backup schedule interval (`KESTREL_BACKUP_SCHEDULE_INTERVAL`, default 45 minutes in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_TWO_FACTOR_GRACE_PERIOD` and given a new default of 122 connections in release 3.6. Before that release, version 3 still used the version 2 name.

## Related

- Import file size limit: see the Import file size limit page for version 3.
- Backup schedule interval: see the Backup schedule interval page for version 3.
