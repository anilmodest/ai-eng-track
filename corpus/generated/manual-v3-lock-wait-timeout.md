---
product: Kestrel Data Runner
version: v3
section: Integrations
---

# Lock wait timeout (Kestrel v3)

This page describes the lock wait timeout setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `KESTREL_LOCK_WAIT_TIMEOUT`, as the environment variable. It takes a whole number of percent. The default is **27 percent**.

```
export KESTREL_LOCK_WAIT_TIMEOUT=27
```

## Upgrading from version 2

`lock_wait_timeout_per`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_LOCK_WAIT_TIMEOUT` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

Every request carries the lock wait timeout that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

The value is reloaded within a few seconds of being changed. No restart is needed, and work already in progress picks up the new value on its next step.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 27 percent. Large ones usually settle between the default and twice the default. Values near the minimum of 2 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_lock_wait_timeout_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 2. The highest accepted value is 88. A value outside that range is rejected and the previous value stays in force, with `E1494: KESTREL_LOCK_WAIT_TIMEOUT out of range` in the log.

## Examples

| Value (percent) | When to use it |
| --- | --- |
| 2 | small installations, or testing |
| 27 | the default; right for most installations |
| 54 | busy installations with spare capacity |
| 88 | the maximum; only with a reason written down |

## Interactions

The lock wait timeout is often changed together with the connection pool size (`KESTREL_CONNECTION_POOL_SIZE`, default 33 minutes in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The lock wait timeout is often changed together with the backup retention (`KESTREL_BACKUP_RETENTION`, default 518 requests per minute in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_LOCK_WAIT_TIMEOUT` and given a new default of 27 percent in release 3.6. Before that release, version 3 still used the version 2 name.

## Related

- Connection pool size: see the Connection pool size page for version 3.
- Backup retention: see the Backup retention page for version 3.
