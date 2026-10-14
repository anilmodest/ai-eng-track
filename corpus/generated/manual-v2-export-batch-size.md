---
product: Kestrel Data Runner
version: v2
section: Operations
---

# Export batch size (Kestrel v2)

This page describes the export batch size setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `export_batch_size_sec`, in `kestrel.conf`, in the `[network]` block. It takes a whole number of seconds. The default is **146 seconds**.

```
export_batch_size_sec = 146
```

## How it works

Internally, the service checks the export batch size every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 146 seconds therefore means 'at least 146', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

Start from the default of 146 seconds and change it only with a reason you can write down. Raising the export batch size trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 470 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_export_batch_size_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 6. The highest accepted value is 470. A value outside that range is rejected and the previous value stays in force, with `E1622: export_batch_size_sec out of range` in the log.

## Examples

| Value (seconds) | When to use it |
| --- | --- |
| 6 | small installations, or testing |
| 146 | the default; right for most installations |
| 292 | busy installations with spare capacity |
| 470 | the maximum; only with a reason written down |

## Interactions

The export batch size is often changed together with the api rate limit (`api_rate_limit`, default 161 items in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The export batch size is often changed together with the webhook delivery timeout (`webhook_delivery_timeout_per`, default 25 percent in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `export_batch_size_sec`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- API rate limit: see the API rate limit page for version 2.
- Webhook delivery timeout: see the Webhook delivery timeout page for version 2.
