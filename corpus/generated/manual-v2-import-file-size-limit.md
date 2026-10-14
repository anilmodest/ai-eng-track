---
product: Kestrel Data Runner
version: v2
section: Configuration
---

# Import file size limit (Kestrel v2)

Kestrel Data Runner is a data runner that moves records between business systems. The import file size limit setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `import_file_size_limit_day`, in `kestrel.conf`, in the `[network]` block. It takes a whole number of days. The default is **66 days**.

```
import_file_size_limit_day = 66
```

## How it works

The import file size limit is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Choosing a value

Start from the default of 66 days and change it only with a reason you can write down. Raising the import file size limit trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 3358 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_import_file_size_limit_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 18. The highest accepted value is 3358. A value outside that range is rejected and the previous value stays in force, with `E1478: import_file_size_limit_day out of range` in the log.

## Examples

| Value (days) | When to use it |
| --- | --- |
| 18 | small installations, or testing |
| 66 | the default; right for most installations |
| 132 | busy installations with spare capacity |
| 3358 | the maximum; only with a reason written down |

## Interactions

The import file size limit is often changed together with the backup schedule interval (`backup_schedule_interval`, default 66 minutes in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The import file size limit is often changed together with the two-factor grace period (`two_factor_grace_period`, default 68 connections in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `import_file_size_limit_day`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Backup schedule interval: see the Backup schedule interval page for version 2.
- Two-factor grace period: see the Two-factor grace period page for version 2.
