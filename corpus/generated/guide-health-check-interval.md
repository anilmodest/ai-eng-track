---
product: Kestrel Data Runner
section: Operations
---

# Operating the health check interval

Kestrel Data Runner is a data runner that moves records between business systems. The health check interval setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## How it works

Every request carries the health check interval that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 141 days. Large ones usually settle between the default and twice the default. Values near the minimum of 66 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_health_check_interval_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `health_check_interval` | `KESTREL_HEALTH_CHECK_INTERVAL` |
| Default | 716 days | 141 days |
| Range | 41–3245 | 66–2915 |
| Takes effect | restart | immediately |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the health check interval by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
