---
product: Kestrel Data Runner
version: v3
section: Integrations
---

# Purge delay (Kestrel v3)

Kestrel Data Runner is a data runner that moves records between business systems. The purge delay setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `KESTREL_PURGE_DELAY`, as the environment variable. It takes a whole number of items. The default is **2444 items**.

```
export KESTREL_PURGE_DELAY=2444
```

## Upgrading from version 2

`purge_delay_ite`, the version 2 setting, is rejected. If it is still present the service refuses to start and logs `E1623: unknown setting purge_delay_ite`. Remove it before upgrading.

## How it works

The purge delay is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Choosing a value

Start from the default of 2444 items and change it only with a reason you can write down. Raising the purge delay trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 8289 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_purge_delay_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 128. The highest accepted value is 8289. A value outside that range is rejected and the previous value stays in force, with `E1623: KESTREL_PURGE_DELAY out of range` in the log.

## Examples

| Value (items) | When to use it |
| --- | --- |
| 128 | small installations, or testing |
| 2444 | the default; right for most installations |
| 4888 | busy installations with spare capacity |
| 8289 | the maximum; only with a reason written down |

## Interactions

The purge delay is often changed together with the connection pool size (`KESTREL_CONNECTION_POOL_SIZE`, default 33 minutes in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The purge delay is often changed together with the backup retention (`KESTREL_BACKUP_RETENTION`, default 518 requests per minute in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_PURGE_DELAY` and given a new default of 2444 items in release 3.2. Before that release, version 3 still used the version 2 name.

## Related

- Connection pool size: see the Connection pool size page for version 3.
- Backup retention: see the Backup retention page for version 3.
