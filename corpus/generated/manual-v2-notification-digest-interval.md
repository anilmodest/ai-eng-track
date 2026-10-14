---
product: Kestrel Data Runner
version: v2
section: Integrations
---

# Notification digest interval (Kestrel v2)

This page describes the notification digest interval setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `notification_digest_interval`, in `kestrel.conf`, in the `[server]` block. It takes a whole number of characters. The default is **297 characters**.

```
notification_digest_interval = 297
```

## How it works

Internally, the service checks the notification digest interval every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 297 characters therefore means 'at least 297', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

Start from the default of 297 characters and change it only with a reason you can write down. Raising the notification digest interval trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 3094 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_notification_digest_interval_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 59. The highest accepted value is 3094. A value outside that range is rejected and the previous value stays in force, with `E1664: notification_digest_interval out of range` in the log.

## Examples

| Value (characters) | When to use it |
| --- | --- |
| 59 | small installations, or testing |
| 297 | the default; right for most installations |
| 594 | busy installations with spare capacity |
| 3094 | the maximum; only with a reason written down |

## Interactions

The notification digest interval is often changed together with the connection pool size (`connection_pool_size_min`, default 55 minutes in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The notification digest interval is often changed together with the backup retention (`backup_retention`, default 496 requests per minute in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `notification_digest_interval`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Connection pool size: see the Connection pool size page for version 2.
- Backup retention: see the Backup retention page for version 2.
