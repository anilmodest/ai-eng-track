---
product: Kestrel Data Runner
version: v3
section: Operations
---

# API rate limit (Kestrel v3)

This page describes the api rate limit setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `KESTREL_API_RATE_LIMIT`, in the admin console, under Settings > Data. It takes a whole number of items. The default is **1542 items**.

The console shows the current value and the default side by side. The same value can be set from the command line with `kestrelctl config set KESTREL_API_RATE_LIMIT 1542`.

## Upgrading from version 2

`api_rate_limit`, the version 2 setting, is rejected. If it is still present the service refuses to start and logs `E1585: unknown setting api_rate_limit`. Remove it before upgrading.

## How it works

The api rate limit is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

Start from the default of 1542 items and change it only with a reason you can write down. Raising the api rate limit trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 7962 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_api_rate_limit_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 152. The highest accepted value is 7962. A value outside that range is rejected and the previous value stays in force, with `E1585: KESTREL_API_RATE_LIMIT out of range` in the log.

## Examples

| Value (items) | When to use it |
| --- | --- |
| 152 | small installations, or testing |
| 1542 | the default; right for most installations |
| 3084 | busy installations with spare capacity |
| 7962 | the maximum; only with a reason written down |

## Interactions

The api rate limit is often changed together with the export batch size (`KESTREL_EXPORT_BATCH_SIZE`, default 57 seconds in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The api rate limit is often changed together with the webhook delivery timeout (`KESTREL_WEBHOOK_DELIVERY_TIMEOUT`, default 3 percent in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_API_RATE_LIMIT` and given a new default of 1542 items in release 3.1. Before that release, version 3 still used the version 2 name.

## Related

- Export batch size: see the Export batch size page for version 3.
- Webhook delivery timeout: see the Webhook delivery timeout page for version 3.
