---
product: Kestrel Data Runner
version: v2
section: Operations
---

# Maintenance window length (Kestrel v2)

This page describes the maintenance window length setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `maintenance_window_length_con`, in `kestrel.conf`, in the `[network]` block. It takes a whole number of connections. The default is **104 connections**.

```
maintenance_window_length_con = 104
```

## How it works

Internally, the service checks the maintenance window length every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 104 connections therefore means 'at least 104', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Choosing a value

Start from the default of 104 connections and change it only with a reason you can write down. Raising the maintenance window length trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 393 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_maintenance_window_length_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 6. The highest accepted value is 393. A value outside that range is rejected and the previous value stays in force, with `E1129: maintenance_window_length_con out of range` in the log.

## Examples

| Value (connections) | When to use it |
| --- | --- |
| 6 | small installations, or testing |
| 104 | the default; right for most installations |
| 208 | busy installations with spare capacity |
| 393 | the maximum; only with a reason written down |

## Interactions

The maintenance window length is often changed together with the export batch size (`export_batch_size_sec`, default 146 seconds in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The maintenance window length is often changed together with the api rate limit (`api_rate_limit`, default 161 items in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `maintenance_window_length_con`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Export batch size: see the Export batch size page for version 2.
- API rate limit: see the API rate limit page for version 2.
