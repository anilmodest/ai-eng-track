---
product: Kestrel Data Runner
version: v2
section: Operations
---

# Transform memory limit (Kestrel v2)

Kestrel Data Runner is a data runner that moves records between business systems. The transform memory limit setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `transform_memory_limit`, in `kestrel.conf`, in the `[source]` block. It takes a whole number of connections. The default is **7 connections**.

```
transform_memory_limit = 7
```

## How it works

Every request carries the transform memory limit that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Choosing a value

Start from the default of 7 connections and change it only with a reason you can write down. Raising the transform memory limit trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 394 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_transform_memory_limit_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 6. The highest accepted value is 394. A value outside that range is rejected and the previous value stays in force, with `E1915: transform_memory_limit out of range` in the log.

## Examples

| Value (connections) | When to use it |
| --- | --- |
| 6 | small installations, or testing |
| 7 | the default; right for most installations |
| 14 | busy installations with spare capacity |
| 394 | the maximum; only with a reason written down |

## Interactions

The transform memory limit is often changed together with the export batch size (`export_batch_size_sec`, default 146 seconds in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The transform memory limit is often changed together with the api rate limit (`api_rate_limit`, default 161 items in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `transform_memory_limit`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Export batch size: see the Export batch size page for version 2.
- API rate limit: see the API rate limit page for version 2.
