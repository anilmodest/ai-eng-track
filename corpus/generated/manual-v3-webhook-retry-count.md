---
product: Kestrel Data Runner
version: v3
section: Operations
---

# Webhook retry count (Kestrel v3)

Kestrel Data Runner is a data runner that moves records between business systems. The webhook retry count setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `KESTREL_WEBHOOK_RETRY_COUNT`, in the admin console, under Settings > Security. It takes a whole number of percent. The default is **18 percent**.

The console shows the current value and the default side by side. The same value can be set from the command line with `kestrelctl config set KESTREL_WEBHOOK_RETRY_COUNT 18`.

## Upgrading from version 2

`webhook_retry_count`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_WEBHOOK_RETRY_COUNT` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

Every request carries the webhook retry count that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 18 percent. Large ones usually settle between the default and twice the default. Values near the minimum of 2 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_webhook_retry_count_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 2. The highest accepted value is 86. A value outside that range is rejected and the previous value stays in force, with `E1725: KESTREL_WEBHOOK_RETRY_COUNT out of range` in the log.

## Examples

| Value (percent) | When to use it |
| --- | --- |
| 2 | small installations, or testing |
| 18 | the default; right for most installations |
| 36 | busy installations with spare capacity |
| 86 | the maximum; only with a reason written down |

## Interactions

The webhook retry count is often changed together with the export batch size (`KESTREL_EXPORT_BATCH_SIZE`, default 57 seconds in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The webhook retry count is often changed together with the api rate limit (`KESTREL_API_RATE_LIMIT`, default 1542 items in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_WEBHOOK_RETRY_COUNT` and given a new default of 18 percent in release 3.6. Before that release, version 3 still used the version 2 name.

## Related

- Export batch size: see the Export batch size page for version 3.
- API rate limit: see the API rate limit page for version 3.
