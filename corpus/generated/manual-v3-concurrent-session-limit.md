---
product: Kestrel Data Runner
version: v3
section: Configuration
---

# Concurrent session limit (Kestrel v3)

In Kestrel Data Runner, the concurrent session limit is a single value measured in percent. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `KESTREL_CONCURRENT_SESSION_LIMIT`, as the environment variable. It takes a whole number of percent. The default is **16 percent**.

```
export KESTREL_CONCURRENT_SESSION_LIMIT=16
```

## Upgrading from version 2

`concurrent_session_limit_per`, the version 2 setting, is no longer used. If it is still present the service **reads it, ignores it and starts normally**. Nothing is written to the log. An installation upgraded from version 2 without this change therefore runs on the version 3 default of 16 percent, not on the value in the old file.

## How it works

The concurrent session limit is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Choosing a value

Start from the default of 16 percent and change it only with a reason you can write down. Raising the concurrent session limit trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 90 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_concurrent_session_limit_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 1. The highest accepted value is 90. A value outside that range is rejected and the previous value stays in force, with `E1306: KESTREL_CONCURRENT_SESSION_LIMIT out of range` in the log.

## Examples

| Value (percent) | When to use it |
| --- | --- |
| 1 | small installations, or testing |
| 16 | the default; right for most installations |
| 32 | busy installations with spare capacity |
| 90 | the maximum; only with a reason written down |

## Interactions

The concurrent session limit is often changed together with the import file size limit (`KESTREL_IMPORT_FILE_SIZE_LIMIT`, default 74 days in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The concurrent session limit is often changed together with the backup schedule interval (`KESTREL_BACKUP_SCHEDULE_INTERVAL`, default 45 minutes in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_CONCURRENT_SESSION_LIMIT` and given a new default of 16 percent in release 3.9. Before that release, version 3 still used the version 2 name.

## Related

- Import file size limit: see the Import file size limit page for version 3.
- Backup schedule interval: see the Backup schedule interval page for version 3.
