---
product: Kestrel Data Runner
version: v2
section: Integrations
---

# Report page size (Kestrel v2)

Kestrel Data Runner is a data runner that moves records between business systems. The report page size setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `report_page_size`, in `kestrel.conf`, in the `[source]` block. It takes a whole number of connections. The default is **65 connections**.

```
report_page_size = 65
```

## How it works

Every request carries the report page size that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 65 connections. Large ones usually settle between the default and twice the default. Values near the minimum of 5 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_report_page_size_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 5. The highest accepted value is 499. A value outside that range is rejected and the previous value stays in force, with `E1717: report_page_size out of range` in the log.

## Examples

| Value (connections) | When to use it |
| --- | --- |
| 5 | small installations, or testing |
| 65 | the default; right for most installations |
| 130 | busy installations with spare capacity |
| 499 | the maximum; only with a reason written down |

## Interactions

The report page size is often changed together with the connection pool size (`connection_pool_size_min`, default 55 minutes in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The report page size is often changed together with the backup retention (`backup_retention`, default 496 requests per minute in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `report_page_size`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Connection pool size: see the Connection pool size page for version 2.
- Backup retention: see the Backup retention page for version 2.
