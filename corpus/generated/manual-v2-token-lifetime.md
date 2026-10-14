---
product: Kestrel Data Runner
version: v2
section: Operations
---

# Token lifetime (Kestrel v2)

In Kestrel Data Runner, the token lifetime is a single value measured in days. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `token_lifetime`, in `kestrel.conf`, in the `[jobs]` block. It takes a whole number of days. The default is **788 days**.

```
token_lifetime = 788
```

## How it works

The token lifetime is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

Start from the default of 788 days and change it only with a reason you can write down. Raising the token lifetime trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 3464 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_token_lifetime_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 39. The highest accepted value is 3464. A value outside that range is rejected and the previous value stays in force, with `E1804: token_lifetime out of range` in the log.

## Examples

| Value (days) | When to use it |
| --- | --- |
| 39 | small installations, or testing |
| 788 | the default; right for most installations |
| 1576 | busy installations with spare capacity |
| 3464 | the maximum; only with a reason written down |

## Interactions

The token lifetime is often changed together with the export batch size (`export_batch_size_sec`, default 146 seconds in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The token lifetime is often changed together with the api rate limit (`api_rate_limit`, default 161 items in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `token_lifetime`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Export batch size: see the Export batch size page for version 2.
- API rate limit: see the API rate limit page for version 2.
