---
product: Kestrel Data Runner
version: v2
section: Configuration
---

# Concurrent session limit (Kestrel v2)

This page describes the concurrent session limit setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `concurrent_session_limit_per`, in `kestrel.conf`, in the `[jobs]` block. It takes a whole number of percent. The default is **26 percent**.

```
concurrent_session_limit_per = 26
```

## How it works

Internally, the service checks the concurrent session limit every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 26 percent therefore means 'at least 26', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

Start from the default of 26 percent and change it only with a reason you can write down. Raising the concurrent session limit trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 90 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_concurrent_session_limit_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 2. The highest accepted value is 90. A value outside that range is rejected and the previous value stays in force, with `E1306: concurrent_session_limit_per out of range` in the log.

## Examples

| Value (percent) | When to use it |
| --- | --- |
| 2 | small installations, or testing |
| 26 | the default; right for most installations |
| 52 | busy installations with spare capacity |
| 90 | the maximum; only with a reason written down |

## Interactions

The concurrent session limit is often changed together with the import file size limit (`import_file_size_limit_day`, default 66 days in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The concurrent session limit is often changed together with the backup schedule interval (`backup_schedule_interval`, default 66 minutes in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `concurrent_session_limit_per`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Import file size limit: see the Import file size limit page for version 2.
- Backup schedule interval: see the Backup schedule interval page for version 2.
