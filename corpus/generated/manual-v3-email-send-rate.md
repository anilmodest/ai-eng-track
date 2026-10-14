---
product: Kestrel Data Runner
version: v3
section: Integrations
---

# Email send rate (Kestrel v3)

Kestrel Data Runner is a data runner that moves records between business systems. The email send rate setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `KESTREL_EMAIL_SEND_RATE`, in the admin console, under Settings > Configuration. It takes a whole number of items. The default is **2131 items**.

The console shows the current value and the default side by side. The same value can be set from the command line with `kestrelctl config set KESTREL_EMAIL_SEND_RATE 2131`.

## Upgrading from version 2

`email_send_rate`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_EMAIL_SEND_RATE` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

Every request carries the email send rate that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

The value is reloaded within a few seconds of being changed. No restart is needed, and work already in progress picks up the new value on its next step.

## Choosing a value

Start from the default of 2131 items and change it only with a reason you can write down. Raising the email send rate trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 8921 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_email_send_rate_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 50. The highest accepted value is 8921. A value outside that range is rejected and the previous value stays in force, with `E1229: KESTREL_EMAIL_SEND_RATE out of range` in the log.

## Examples

| Value (items) | When to use it |
| --- | --- |
| 50 | small installations, or testing |
| 2131 | the default; right for most installations |
| 4262 | busy installations with spare capacity |
| 8921 | the maximum; only with a reason written down |

## Interactions

The email send rate is often changed together with the connection pool size (`KESTREL_CONNECTION_POOL_SIZE`, default 33 minutes in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The email send rate is often changed together with the backup retention (`KESTREL_BACKUP_RETENTION`, default 518 requests per minute in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_EMAIL_SEND_RATE` and given a new default of 2131 items in release 3.2. Before that release, version 3 still used the version 2 name.

## Related

- Connection pool size: see the Connection pool size page for version 3.
- Backup retention: see the Backup retention page for version 3.
