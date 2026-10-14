---
product: Kestrel Data Runner
version: v2
section: Operations
---

# API rate limit (Kestrel v2)

This page describes the api rate limit setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `api_rate_limit`, in `kestrel.conf`, in the `[jobs]` block. It takes a whole number of items. The default is **161 items**.

```
api_rate_limit = 161
```

## How it works

Internally, the service checks the api rate limit every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 161 items therefore means 'at least 161', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Choosing a value

Start from the default of 161 items and change it only with a reason you can write down. Raising the api rate limit trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 7564 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_api_rate_limit_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 98. The highest accepted value is 7564. A value outside that range is rejected and the previous value stays in force, with `E1585: api_rate_limit out of range` in the log.

## Examples

| Value (items) | When to use it |
| --- | --- |
| 98 | small installations, or testing |
| 161 | the default; right for most installations |
| 322 | busy installations with spare capacity |
| 7564 | the maximum; only with a reason written down |

## Interactions

The api rate limit is often changed together with the export batch size (`export_batch_size_sec`, default 146 seconds in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The api rate limit is often changed together with the webhook delivery timeout (`webhook_delivery_timeout_per`, default 25 percent in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `api_rate_limit`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Export batch size: see the Export batch size page for version 2.
- Webhook delivery timeout: see the Webhook delivery timeout page for version 2.
