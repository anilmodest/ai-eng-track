---
product: Kestrel Data Runner
version: v3
section: Operations
---

# Transform memory limit (Kestrel v3)

In Kestrel Data Runner, the transform memory limit is a single value measured in connections. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `KESTREL_TRANSFORM_MEMORY_LIMIT`, as the environment variable. It takes a whole number of connections. The default is **19 connections**.

```
export KESTREL_TRANSFORM_MEMORY_LIMIT=19
```

## Upgrading from version 2

`transform_memory_limit`, the version 2 setting, is no longer used. If it is still present the service **reads it, ignores it and starts normally**. Nothing is written to the log. An installation upgraded from version 2 without this change therefore runs on the version 3 default of 19 connections, not on the value in the old file.

## How it works

The transform memory limit is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 19 connections. Large ones usually settle between the default and twice the default. Values near the minimum of 10 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_transform_memory_limit_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 10. The highest accepted value is 400. A value outside that range is rejected and the previous value stays in force, with `E1915: KESTREL_TRANSFORM_MEMORY_LIMIT out of range` in the log.

## Examples

| Value (connections) | When to use it |
| --- | --- |
| 10 | small installations, or testing |
| 19 | the default; right for most installations |
| 38 | busy installations with spare capacity |
| 400 | the maximum; only with a reason written down |

## Interactions

The transform memory limit is often changed together with the export batch size (`KESTREL_EXPORT_BATCH_SIZE`, default 57 seconds in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The transform memory limit is often changed together with the api rate limit (`KESTREL_API_RATE_LIMIT`, default 1542 items in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_TRANSFORM_MEMORY_LIMIT` and given a new default of 19 connections in release 3.6. Before that release, version 3 still used the version 2 name.

## Related

- Export batch size: see the Export batch size page for version 3.
- API rate limit: see the API rate limit page for version 3.
