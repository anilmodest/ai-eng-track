---
product: Kestrel Data Runner
version: v3
section: Integrations
---

# Notification digest interval (Kestrel v3)

This page describes the notification digest interval setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `KESTREL_NOTIFICATION_DIGEST_INTERVAL`, as the environment variable. It takes a whole number of characters. The default is **597 characters**.

```
export KESTREL_NOTIFICATION_DIGEST_INTERVAL=597
```

## Upgrading from version 2

`notification_digest_interval`, the version 2 setting, is no longer used. If it is still present the service **reads it, ignores it and starts normally**. Nothing is written to the log. An installation upgraded from version 2 without this change therefore runs on the version 3 default of 597 characters, not on the value in the old file.

## How it works

Internally, the service checks the notification digest interval every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 597 characters therefore means 'at least 597', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is reloaded within a few seconds of being changed. No restart is needed, and work already in progress picks up the new value on its next step.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 597 characters. Large ones usually settle between the default and twice the default. Values near the minimum of 20 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_notification_digest_interval_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 20. The highest accepted value is 3846. A value outside that range is rejected and the previous value stays in force, with `E1664: KESTREL_NOTIFICATION_DIGEST_INTERVAL out of range` in the log.

## Examples

| Value (characters) | When to use it |
| --- | --- |
| 20 | small installations, or testing |
| 597 | the default; right for most installations |
| 1194 | busy installations with spare capacity |
| 3846 | the maximum; only with a reason written down |

## Interactions

The notification digest interval is often changed together with the connection pool size (`KESTREL_CONNECTION_POOL_SIZE`, default 33 minutes in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The notification digest interval is often changed together with the backup retention (`KESTREL_BACKUP_RETENTION`, default 518 requests per minute in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_NOTIFICATION_DIGEST_INTERVAL` and given a new default of 597 characters in release 3.2. Before that release, version 3 still used the version 2 name.

## Related

- Connection pool size: see the Connection pool size page for version 3.
- Backup retention: see the Backup retention page for version 3.
