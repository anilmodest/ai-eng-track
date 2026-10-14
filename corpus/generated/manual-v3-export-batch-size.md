---
product: Kestrel Data Runner
version: v3
section: Operations
---

# Export batch size (Kestrel v3)

This page describes the export batch size setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `KESTREL_EXPORT_BATCH_SIZE`, as the environment variable. It takes a whole number of seconds. The default is **57 seconds**.

```
export KESTREL_EXPORT_BATCH_SIZE=57
```

## Upgrading from version 2

`export_batch_size_sec`, the version 2 setting, is rejected. If it is still present the service refuses to start and logs `E1622: unknown setting export_batch_size_sec`. Remove it before upgrading.

## How it works

The export batch size is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Choosing a value

Start from the default of 57 seconds and change it only with a reason you can write down. Raising the export batch size trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 571 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_export_batch_size_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 7. The highest accepted value is 571. A value outside that range is rejected and the previous value stays in force, with `E1622: KESTREL_EXPORT_BATCH_SIZE out of range` in the log.

## Examples

| Value (seconds) | When to use it |
| --- | --- |
| 7 | small installations, or testing |
| 57 | the default; right for most installations |
| 114 | busy installations with spare capacity |
| 571 | the maximum; only with a reason written down |

## Interactions

The export batch size is often changed together with the api rate limit (`KESTREL_API_RATE_LIMIT`, default 1542 items in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The export batch size is often changed together with the webhook delivery timeout (`KESTREL_WEBHOOK_DELIVERY_TIMEOUT`, default 3 percent in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_EXPORT_BATCH_SIZE` and given a new default of 57 seconds in release 3.1. Before that release, version 3 still used the version 2 name.

## Related

- API rate limit: see the API rate limit page for version 3.
- Webhook delivery timeout: see the Webhook delivery timeout page for version 3.
