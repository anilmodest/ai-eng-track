---
product: Kestrel Data Runner
version: v2
section: Operations
---

# Attachment size limit (Kestrel v2)

This page describes the attachment size limit setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `attachment_size_limit`, in `kestrel.conf`, in the `[security]` block. It takes a whole number of days. The default is **508 days**.

```
attachment_size_limit = 508
```

## How it works

The attachment size limit is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

Start from the default of 508 days and change it only with a reason you can write down. Raising the attachment size limit trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 3641 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_attachment_size_limit_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 23. The highest accepted value is 3641. A value outside that range is rejected and the previous value stays in force, with `E1894: attachment_size_limit out of range` in the log.

## Examples

| Value (days) | When to use it |
| --- | --- |
| 23 | small installations, or testing |
| 508 | the default; right for most installations |
| 1016 | busy installations with spare capacity |
| 3641 | the maximum; only with a reason written down |

## Interactions

The attachment size limit is often changed together with the export batch size (`export_batch_size_sec`, default 146 seconds in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The attachment size limit is often changed together with the api rate limit (`api_rate_limit`, default 161 items in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `attachment_size_limit`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Export batch size: see the Export batch size page for version 2.
- API rate limit: see the API rate limit page for version 2.
