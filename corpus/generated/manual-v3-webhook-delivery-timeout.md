---
product: Kestrel Data Runner
version: v3
section: Operations
---

# Webhook delivery timeout (Kestrel v3)

Kestrel Data Runner is a data runner that moves records between business systems. The webhook delivery timeout setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `KESTREL_WEBHOOK_DELIVERY_TIMEOUT`, as the environment variable. It takes a whole number of percent. The default is **3 percent**.

```
export KESTREL_WEBHOOK_DELIVERY_TIMEOUT=3
```

## Upgrading from version 2

`webhook_delivery_timeout_per`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_WEBHOOK_DELIVERY_TIMEOUT` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

Internally, the service checks the webhook delivery timeout every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 3 percent therefore means 'at least 3', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Choosing a value

Start from the default of 3 percent and change it only with a reason you can write down. Raising the webhook delivery timeout trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 94 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_webhook_delivery_timeout_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 2. The highest accepted value is 94. A value outside that range is rejected and the previous value stays in force, with `E1220: KESTREL_WEBHOOK_DELIVERY_TIMEOUT out of range` in the log.

## Examples

| Value (percent) | When to use it |
| --- | --- |
| 2 | small installations, or testing |
| 3 | the default; right for most installations |
| 6 | busy installations with spare capacity |
| 94 | the maximum; only with a reason written down |

## Interactions

The webhook delivery timeout is often changed together with the export batch size (`KESTREL_EXPORT_BATCH_SIZE`, default 57 seconds in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The webhook delivery timeout is often changed together with the api rate limit (`KESTREL_API_RATE_LIMIT`, default 1542 items in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_WEBHOOK_DELIVERY_TIMEOUT` and given a new default of 3 percent in release 3.4. Before that release, version 3 still used the version 2 name.

## Related

- Export batch size: see the Export batch size page for version 3.
- API rate limit: see the API rate limit page for version 3.
