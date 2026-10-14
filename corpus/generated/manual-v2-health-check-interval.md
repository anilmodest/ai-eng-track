---
product: Kestrel Data Runner
version: v2
section: Configuration
---

# Health check interval (Kestrel v2)

This page describes the health check interval setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `health_check_interval`, in `kestrel.conf`, in the `[network]` block. It takes a whole number of days. The default is **716 days**.

```
health_check_interval = 716
```

## How it works

The health check interval is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

Start from the default of 716 days and change it only with a reason you can write down. Raising the health check interval trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 3245 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_health_check_interval_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 41. The highest accepted value is 3245. A value outside that range is rejected and the previous value stays in force, with `E1773: health_check_interval out of range` in the log.

## Examples

| Value (days) | When to use it |
| --- | --- |
| 41 | small installations, or testing |
| 716 | the default; right for most installations |
| 1432 | busy installations with spare capacity |
| 3245 | the maximum; only with a reason written down |

## Interactions

The health check interval is often changed together with the import file size limit (`import_file_size_limit_day`, default 66 days in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The health check interval is often changed together with the backup schedule interval (`backup_schedule_interval`, default 66 minutes in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `health_check_interval`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Import file size limit: see the Import file size limit page for version 2.
- Backup schedule interval: see the Backup schedule interval page for version 2.
