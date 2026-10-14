---
product: Kestrel Data Runner
version: v3
section: Operations
---

# Maintenance window length (Kestrel v3)

This page describes the maintenance window length setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `KESTREL_MAINTENANCE_WINDOW_LENGTH`, in the admin console, under Settings > Operations. It takes a whole number of connections. The default is **87 connections**.

The console shows the current value and the default side by side. The same value can be set from the command line with `kestrelctl config set KESTREL_MAINTENANCE_WINDOW_LENGTH 87`.

## Upgrading from version 2

`maintenance_window_length_con`, the version 2 setting, is rejected. If it is still present the service refuses to start and logs `E1129: unknown setting maintenance_window_length_con`. Remove it before upgrading.

## How it works

Internally, the service checks the maintenance window length every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 87 connections therefore means 'at least 87', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

Start from the default of 87 connections and change it only with a reason you can write down. Raising the maintenance window length trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 482 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_maintenance_window_length_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 1. The highest accepted value is 482. A value outside that range is rejected and the previous value stays in force, with `E1129: KESTREL_MAINTENANCE_WINDOW_LENGTH out of range` in the log.

## Examples

| Value (connections) | When to use it |
| --- | --- |
| 1 | small installations, or testing |
| 87 | the default; right for most installations |
| 174 | busy installations with spare capacity |
| 482 | the maximum; only with a reason written down |

## Interactions

The maintenance window length is often changed together with the export batch size (`KESTREL_EXPORT_BATCH_SIZE`, default 57 seconds in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The maintenance window length is often changed together with the api rate limit (`KESTREL_API_RATE_LIMIT`, default 1542 items in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_MAINTENANCE_WINDOW_LENGTH` and given a new default of 87 connections in release 3.4. Before that release, version 3 still used the version 2 name.

## Related

- Export batch size: see the Export batch size page for version 3.
- API rate limit: see the API rate limit page for version 3.
