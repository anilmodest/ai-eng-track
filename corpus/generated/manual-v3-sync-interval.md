---
product: Kestrel Data Runner
version: v3
section: Operations
---

# Sync interval (Kestrel v3)

This page describes the sync interval setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `KESTREL_SYNC_INTERVAL`, as the environment variable. It takes a whole number of megabytes. The default is **383 megabytes**.

```
export KESTREL_SYNC_INTERVAL=383
```

## Upgrading from version 2

`sync_interval`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_SYNC_INTERVAL` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

Internally, the service checks the sync interval every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 383 megabytes therefore means 'at least 383', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Choosing a value

Start from the default of 383 megabytes and change it only with a reason you can write down. Raising the sync interval trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 1577 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_sync_interval_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 31. The highest accepted value is 1577. A value outside that range is rejected and the previous value stays in force, with `E1584: KESTREL_SYNC_INTERVAL out of range` in the log.

## Examples

| Value (megabytes) | When to use it |
| --- | --- |
| 31 | small installations, or testing |
| 383 | the default; right for most installations |
| 766 | busy installations with spare capacity |
| 1577 | the maximum; only with a reason written down |

## Interactions

The sync interval is often changed together with the export batch size (`KESTREL_EXPORT_BATCH_SIZE`, default 57 seconds in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The sync interval is often changed together with the api rate limit (`KESTREL_API_RATE_LIMIT`, default 1542 items in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_SYNC_INTERVAL` and given a new default of 383 megabytes in release 3.2. Before that release, version 3 still used the version 2 name.

## Related

- Export batch size: see the Export batch size page for version 3.
- API rate limit: see the API rate limit page for version 3.
