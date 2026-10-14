---
product: Kestrel Data Runner
version: v2
section: Operations
---

# Webhook delivery timeout (Kestrel v2)

In Kestrel Data Runner, the webhook delivery timeout is a single value measured in percent. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `webhook_delivery_timeout_per`, in `kestrel.conf`, in the `[jobs]` block. It takes a whole number of percent. The default is **25 percent**.

```
webhook_delivery_timeout_per = 25
```

## How it works

Every request carries the webhook delivery timeout that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 25 percent. Large ones usually settle between the default and twice the default. Values near the minimum of 1 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_webhook_delivery_timeout_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 1. The highest accepted value is 93. A value outside that range is rejected and the previous value stays in force, with `E1220: webhook_delivery_timeout_per out of range` in the log.

## Examples

| Value (percent) | When to use it |
| --- | --- |
| 1 | small installations, or testing |
| 25 | the default; right for most installations |
| 50 | busy installations with spare capacity |
| 93 | the maximum; only with a reason written down |

## Interactions

The webhook delivery timeout is often changed together with the export batch size (`export_batch_size_sec`, default 146 seconds in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The webhook delivery timeout is often changed together with the api rate limit (`api_rate_limit`, default 161 items in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `webhook_delivery_timeout_per`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Export batch size: see the Export batch size page for version 2.
- API rate limit: see the API rate limit page for version 2.
