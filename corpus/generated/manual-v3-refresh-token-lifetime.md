---
product: Kestrel Data Runner
version: v3
section: Operations
---

# Refresh token lifetime (Kestrel v3)

This page describes the refresh token lifetime setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `KESTREL_REFRESH_TOKEN_LIFETIME`, as the environment variable. It takes a whole number of percent. The default is **15 percent**.

```
export KESTREL_REFRESH_TOKEN_LIFETIME=15
```

## Upgrading from version 2

`refresh_token_lifetime`, the version 2 setting, is rejected. If it is still present the service refuses to start and logs `E1709: unknown setting refresh_token_lifetime`. Remove it before upgrading.

## How it works

The refresh token lifetime is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

Start from the default of 15 percent and change it only with a reason you can write down. Raising the refresh token lifetime trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 83 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_refresh_token_lifetime_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 2. The highest accepted value is 83. A value outside that range is rejected and the previous value stays in force, with `E1709: KESTREL_REFRESH_TOKEN_LIFETIME out of range` in the log.

## Examples

| Value (percent) | When to use it |
| --- | --- |
| 2 | small installations, or testing |
| 15 | the default; right for most installations |
| 30 | busy installations with spare capacity |
| 83 | the maximum; only with a reason written down |

## Interactions

The refresh token lifetime is often changed together with the export batch size (`KESTREL_EXPORT_BATCH_SIZE`, default 57 seconds in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The refresh token lifetime is often changed together with the api rate limit (`KESTREL_API_RATE_LIMIT`, default 1542 items in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_REFRESH_TOKEN_LIFETIME` and given a new default of 15 percent in release 3.4. Before that release, version 3 still used the version 2 name.

## Related

- Export batch size: see the Export batch size page for version 3.
- API rate limit: see the API rate limit page for version 3.
