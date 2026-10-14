---
product: Kestrel Data Runner
version: v3
section: Operations
---

# Bulk update limit (Kestrel v3)

In Kestrel Data Runner, the bulk update limit is a single value measured in hours. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `KESTREL_BULK_UPDATE_LIMIT`, as the environment variable. It takes a whole number of hours. The default is **9 hours**.

```
export KESTREL_BULK_UPDATE_LIMIT=9
```

## Upgrading from version 2

`bulk_update_limit`, the version 2 setting, is rejected. If it is still present the service refuses to start and logs `E1816: unknown setting bulk_update_limit`. Remove it before upgrading.

## How it works

Internally, the service checks the bulk update limit every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 9 hours therefore means 'at least 9', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Choosing a value

Start from the default of 9 hours and change it only with a reason you can write down. Raising the bulk update limit trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 128 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_bulk_update_limit_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 4. The highest accepted value is 128. A value outside that range is rejected and the previous value stays in force, with `E1816: KESTREL_BULK_UPDATE_LIMIT out of range` in the log.

## Examples

| Value (hours) | When to use it |
| --- | --- |
| 4 | small installations, or testing |
| 9 | the default; right for most installations |
| 18 | busy installations with spare capacity |
| 128 | the maximum; only with a reason written down |

## Interactions

The bulk update limit is often changed together with the export batch size (`KESTREL_EXPORT_BATCH_SIZE`, default 57 seconds in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The bulk update limit is often changed together with the api rate limit (`KESTREL_API_RATE_LIMIT`, default 1542 items in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_BULK_UPDATE_LIMIT` and given a new default of 9 hours in release 3.6. Before that release, version 3 still used the version 2 name.

## Related

- Export batch size: see the Export batch size page for version 3.
- API rate limit: see the API rate limit page for version 3.
