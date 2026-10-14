---
product: Kestrel Data Runner
version: v3
section: Data
---

# Source poll interval (Kestrel v3)

In Kestrel Data Runner, the source poll interval is a single value measured in minutes. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `KESTREL_SOURCE_POLL_INTERVAL`, as the environment variable. It takes a whole number of minutes. The default is **29 minutes**.

```
export KESTREL_SOURCE_POLL_INTERVAL=29
```

## Upgrading from version 2

`source_poll_interval`, the version 2 setting, is no longer used. If it is still present the service **reads it, ignores it and starts normally**. Nothing is written to the log. An installation upgraded from version 2 without this change therefore runs on the version 3 default of 29 minutes, not on the value in the old file.

## How it works

Every request carries the source poll interval that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 29 minutes. Large ones usually settle between the default and twice the default. Values near the minimum of 5 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_source_poll_interval_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 5. The highest accepted value is 193. A value outside that range is rejected and the previous value stays in force, with `E1260: KESTREL_SOURCE_POLL_INTERVAL out of range` in the log.

## Examples

| Value (minutes) | When to use it |
| --- | --- |
| 5 | small installations, or testing |
| 29 | the default; right for most installations |
| 58 | busy installations with spare capacity |
| 193 | the maximum; only with a reason written down |

## Interactions

The source poll interval is often changed together with the request timeout (`KESTREL_REQUEST_TIMEOUT`, default 7 hours in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The source poll interval is often changed together with the audit log retention (`KESTREL_AUDIT_LOG_RETENTION`, default 129 connections in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_SOURCE_POLL_INTERVAL` and given a new default of 29 minutes in release 3.2. Before that release, version 3 still used the version 2 name.

## Related

- Request timeout: see the Request timeout page for version 3.
- Audit log retention: see the Audit log retention page for version 3.
