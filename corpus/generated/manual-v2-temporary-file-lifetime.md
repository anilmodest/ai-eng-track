---
product: Kestrel Data Runner
version: v2
section: Operations
---

# Temporary file lifetime (Kestrel v2)

Kestrel Data Runner is a data runner that moves records between business systems. The temporary file lifetime setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `temporary_file_lifetime_sec`, in `kestrel.conf`, in the `[server]` block. It takes a whole number of seconds. The default is **134 seconds**.

```
temporary_file_lifetime_sec = 134
```

## How it works

Every request carries the temporary file lifetime that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 134 seconds. Large ones usually settle between the default and twice the default. Values near the minimum of 7 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_temporary_file_lifetime_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 7. The highest accepted value is 533. A value outside that range is rejected and the previous value stays in force, with `E1489: temporary_file_lifetime_sec out of range` in the log.

## Examples

| Value (seconds) | When to use it |
| --- | --- |
| 7 | small installations, or testing |
| 134 | the default; right for most installations |
| 268 | busy installations with spare capacity |
| 533 | the maximum; only with a reason written down |

## Interactions

The temporary file lifetime is often changed together with the export batch size (`export_batch_size_sec`, default 146 seconds in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The temporary file lifetime is often changed together with the api rate limit (`api_rate_limit`, default 161 items in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `temporary_file_lifetime_sec`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Export batch size: see the Export batch size page for version 2.
- API rate limit: see the API rate limit page for version 2.
