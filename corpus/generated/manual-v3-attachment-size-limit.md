---
product: Kestrel Data Runner
version: v3
section: Operations
---

# Attachment size limit (Kestrel v3)

This page describes the attachment size limit setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `KESTREL_ATTACHMENT_SIZE_LIMIT`, as the environment variable. It takes a whole number of days. The default is **499 days**.

```
export KESTREL_ATTACHMENT_SIZE_LIMIT=499
```

## Upgrading from version 2

`attachment_size_limit`, the version 2 setting, is rejected. If it is still present the service refuses to start and logs `E1894: unknown setting attachment_size_limit`. Remove it before upgrading.

## How it works

Every request carries the attachment size limit that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Choosing a value

Start from the default of 499 days and change it only with a reason you can write down. Raising the attachment size limit trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 3628 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_attachment_size_limit_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 46. The highest accepted value is 3628. A value outside that range is rejected and the previous value stays in force, with `E1894: KESTREL_ATTACHMENT_SIZE_LIMIT out of range` in the log.

## Examples

| Value (days) | When to use it |
| --- | --- |
| 46 | small installations, or testing |
| 499 | the default; right for most installations |
| 998 | busy installations with spare capacity |
| 3628 | the maximum; only with a reason written down |

## Interactions

The attachment size limit is often changed together with the export batch size (`KESTREL_EXPORT_BATCH_SIZE`, default 57 seconds in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The attachment size limit is often changed together with the api rate limit (`KESTREL_API_RATE_LIMIT`, default 1542 items in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_ATTACHMENT_SIZE_LIMIT` and given a new default of 499 days in release 3.8. Before that release, version 3 still used the version 2 name.

## Related

- Export batch size: see the Export batch size page for version 3.
- API rate limit: see the API rate limit page for version 3.
