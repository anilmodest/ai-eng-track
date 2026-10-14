---
product: Kestrel Data Runner
version: v3
section: Integrations
---

# Password expiry (Kestrel v3)

Kestrel Data Runner is a data runner that moves records between business systems. The password expiry setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `KESTREL_PASSWORD_EXPIRY`, as the environment variable. It takes a whole number of connections. The default is **38 connections**.

```
export KESTREL_PASSWORD_EXPIRY=38
```

## Upgrading from version 2

`password_expiry`, the version 2 setting, is no longer used. If it is still present the service **reads it, ignores it and starts normally**. Nothing is written to the log. An installation upgraded from version 2 without this change therefore runs on the version 3 default of 38 connections, not on the value in the old file.

## How it works

Internally, the service checks the password expiry every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 38 connections therefore means 'at least 38', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Choosing a value

Start from the default of 38 connections and change it only with a reason you can write down. Raising the password expiry trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 420 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_password_expiry_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 3. The highest accepted value is 420. A value outside that range is rejected and the previous value stays in force, with `E1244: KESTREL_PASSWORD_EXPIRY out of range` in the log.

## Examples

| Value (connections) | When to use it |
| --- | --- |
| 3 | small installations, or testing |
| 38 | the default; right for most installations |
| 76 | busy installations with spare capacity |
| 420 | the maximum; only with a reason written down |

## Interactions

The password expiry is often changed together with the connection pool size (`KESTREL_CONNECTION_POOL_SIZE`, default 33 minutes in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The password expiry is often changed together with the backup retention (`KESTREL_BACKUP_RETENTION`, default 518 requests per minute in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_PASSWORD_EXPIRY` and given a new default of 38 connections in release 3.6. Before that release, version 3 still used the version 2 name.

## Related

- Connection pool size: see the Connection pool size page for version 3.
- Backup retention: see the Backup retention page for version 3.
