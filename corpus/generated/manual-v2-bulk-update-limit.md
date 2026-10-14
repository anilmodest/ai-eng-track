---
product: Kestrel Data Runner
version: v2
section: Operations
---

# Bulk update limit (Kestrel v2)

This page describes the bulk update limit setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `bulk_update_limit`, in `kestrel.conf`, in the `[server]` block. It takes a whole number of hours. The default is **42 hours**.

```
bulk_update_limit = 42
```

## How it works

The bulk update limit is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 42 hours. Large ones usually settle between the default and twice the default. Values near the minimum of 4 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_bulk_update_limit_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 4. The highest accepted value is 164. A value outside that range is rejected and the previous value stays in force, with `E1816: bulk_update_limit out of range` in the log.

## Examples

| Value (hours) | When to use it |
| --- | --- |
| 4 | small installations, or testing |
| 42 | the default; right for most installations |
| 84 | busy installations with spare capacity |
| 164 | the maximum; only with a reason written down |

## Interactions

The bulk update limit is often changed together with the export batch size (`export_batch_size_sec`, default 146 seconds in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The bulk update limit is often changed together with the api rate limit (`api_rate_limit`, default 161 items in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `bulk_update_limit`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Export batch size: see the Export batch size page for version 2.
- API rate limit: see the API rate limit page for version 2.
