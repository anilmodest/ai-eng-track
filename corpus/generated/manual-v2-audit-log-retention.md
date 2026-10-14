---
product: Kestrel Data Runner
version: v2
section: Data
---

# Audit log retention (Kestrel v2)

Kestrel Data Runner is a data runner that moves records between business systems. The audit log retention setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `audit_log_retention`, in `kestrel.conf`, in the `[source]` block. It takes a whole number of connections. The default is **22 connections**.

```
audit_log_retention = 22
```

## How it works

Every request carries the audit log retention that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 22 connections. Large ones usually settle between the default and twice the default. Values near the minimum of 7 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_audit_log_retention_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 7. The highest accepted value is 406. A value outside that range is rejected and the previous value stays in force, with `E1710: audit_log_retention out of range` in the log.

## Examples

| Value (connections) | When to use it |
| --- | --- |
| 7 | small installations, or testing |
| 22 | the default; right for most installations |
| 44 | busy installations with spare capacity |
| 406 | the maximum; only with a reason written down |

## Interactions

The audit log retention is often changed together with the request timeout (`request_timeout`, default 2 hours in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The audit log retention is often changed together with the metrics flush interval (`metrics_flush_interval`, default 52 hours in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `audit_log_retention`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Request timeout: see the Request timeout page for version 2.
- Metrics flush interval: see the Metrics flush interval page for version 2.
