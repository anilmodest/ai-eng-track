---
product: Kestrel Data Runner
version: v3
section: Operations
---

# Temporary file lifetime (Kestrel v3)

Kestrel Data Runner is a data runner that moves records between business systems. The temporary file lifetime setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `KESTREL_TEMPORARY_FILE_LIFETIME`, as the environment variable. It takes a whole number of seconds. The default is **162 seconds**.

```
export KESTREL_TEMPORARY_FILE_LIFETIME=162
```

## Upgrading from version 2

`temporary_file_lifetime_sec`, the version 2 setting, is no longer used. If it is still present the service **reads it, ignores it and starts normally**. Nothing is written to the log. An installation upgraded from version 2 without this change therefore runs on the version 3 default of 162 seconds, not on the value in the old file.

## How it works

Every request carries the temporary file lifetime that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 162 seconds. Large ones usually settle between the default and twice the default. Values near the minimum of 8 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_temporary_file_lifetime_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 8. The highest accepted value is 566. A value outside that range is rejected and the previous value stays in force, with `E1489: KESTREL_TEMPORARY_FILE_LIFETIME out of range` in the log.

## Examples

| Value (seconds) | When to use it |
| --- | --- |
| 8 | small installations, or testing |
| 162 | the default; right for most installations |
| 324 | busy installations with spare capacity |
| 566 | the maximum; only with a reason written down |

## Interactions

The temporary file lifetime is often changed together with the export batch size (`KESTREL_EXPORT_BATCH_SIZE`, default 57 seconds in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The temporary file lifetime is often changed together with the api rate limit (`KESTREL_API_RATE_LIMIT`, default 1542 items in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_TEMPORARY_FILE_LIFETIME` and given a new default of 162 seconds in release 3.6. Before that release, version 3 still used the version 2 name.

## Related

- Export batch size: see the Export batch size page for version 3.
- API rate limit: see the API rate limit page for version 3.
