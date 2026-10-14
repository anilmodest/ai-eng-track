---
product: Kestrel Data Runner
version: v3
section: Integrations
---

# Backup retention (Kestrel v3)

In Kestrel Data Runner, the backup retention is a single value measured in requests per minute. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `KESTREL_BACKUP_RETENTION`, as the environment variable. It takes a whole number of requests per minute. The default is **518 requests per minute**.

```
export KESTREL_BACKUP_RETENTION=518
```

## Upgrading from version 2

`backup_retention`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_BACKUP_RETENTION` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

The backup retention is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 518 requests per minute. Large ones usually settle between the default and twice the default. Values near the minimum of 110 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_backup_retention_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 110. The highest accepted value is 5059. A value outside that range is rejected and the previous value stays in force, with `E1956: KESTREL_BACKUP_RETENTION out of range` in the log.

## Examples

| Value (requests per minute) | When to use it |
| --- | --- |
| 110 | small installations, or testing |
| 518 | the default; right for most installations |
| 1036 | busy installations with spare capacity |
| 5059 | the maximum; only with a reason written down |

## Interactions

The backup retention is often changed together with the connection pool size (`KESTREL_CONNECTION_POOL_SIZE`, default 33 minutes in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The backup retention is often changed together with the password expiry (`KESTREL_PASSWORD_EXPIRY`, default 38 connections in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_BACKUP_RETENTION` and given a new default of 518 requests per minute in release 3.9. Before that release, version 3 still used the version 2 name.

## Related

- Connection pool size: see the Connection pool size page for version 3.
- Password expiry: see the Password expiry page for version 3.
