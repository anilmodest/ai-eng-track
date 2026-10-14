---
product: Kestrel Data Runner
version: v2
section: Configuration
---

# Backup schedule interval (Kestrel v2)

This page describes the backup schedule interval setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `backup_schedule_interval`, in `kestrel.conf`, in the `[security]` block. It takes a whole number of minutes. The default is **66 minutes**.

```
backup_schedule_interval = 66
```

## How it works

Every request carries the backup schedule interval that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 66 minutes. Large ones usually settle between the default and twice the default. Values near the minimum of 1 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_backup_schedule_interval_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 1. The highest accepted value is 229. A value outside that range is rejected and the previous value stays in force, with `E1535: backup_schedule_interval out of range` in the log.

## Examples

| Value (minutes) | When to use it |
| --- | --- |
| 1 | small installations, or testing |
| 66 | the default; right for most installations |
| 132 | busy installations with spare capacity |
| 229 | the maximum; only with a reason written down |

## Interactions

The backup schedule interval is often changed together with the import file size limit (`import_file_size_limit_day`, default 66 days in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The backup schedule interval is often changed together with the two-factor grace period (`two_factor_grace_period`, default 68 connections in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `backup_schedule_interval`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Import file size limit: see the Import file size limit page for version 2.
- Two-factor grace period: see the Two-factor grace period page for version 2.
