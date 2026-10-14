---
product: Kestrel Data Runner
version: v3
section: Integrations
---

# Report page size (Kestrel v3)

This page describes the report page size setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `KESTREL_REPORT_PAGE_SIZE`, as the environment variable. It takes a whole number of connections. The default is **157 connections**.

```
export KESTREL_REPORT_PAGE_SIZE=157
```

## Upgrading from version 2

`report_page_size`, the version 2 setting, is rejected. If it is still present the service refuses to start and logs `E1717: unknown setting report_page_size`. Remove it before upgrading.

## How it works

Internally, the service checks the report page size every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 157 connections therefore means 'at least 157', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Choosing a value

Start from the default of 157 connections and change it only with a reason you can write down. Raising the report page size trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 499 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_report_page_size_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 10. The highest accepted value is 499. A value outside that range is rejected and the previous value stays in force, with `E1717: KESTREL_REPORT_PAGE_SIZE out of range` in the log.

## Examples

| Value (connections) | When to use it |
| --- | --- |
| 10 | small installations, or testing |
| 157 | the default; right for most installations |
| 314 | busy installations with spare capacity |
| 499 | the maximum; only with a reason written down |

## Interactions

The report page size is often changed together with the connection pool size (`KESTREL_CONNECTION_POOL_SIZE`, default 33 minutes in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The report page size is often changed together with the backup retention (`KESTREL_BACKUP_RETENTION`, default 518 requests per minute in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_REPORT_PAGE_SIZE` and given a new default of 157 connections in release 3.2. Before that release, version 3 still used the version 2 name.

## Related

- Connection pool size: see the Connection pool size page for version 3.
- Backup retention: see the Backup retention page for version 3.
