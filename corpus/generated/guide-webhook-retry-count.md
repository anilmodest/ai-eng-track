---
product: Kestrel Data Runner
section: Operations
---

# Operating the webhook retry count

In Kestrel Data Runner, the webhook retry count is a single value measured in percent. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## How it works

Every request carries the webhook retry count that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 18 percent. Large ones usually settle between the default and twice the default. Values near the minimum of 2 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_webhook_retry_count_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `webhook_retry_count` | `KESTREL_WEBHOOK_RETRY_COUNT` |
| Default | 12 percent | 18 percent |
| Range | 1–97 | 2–86 |
| Takes effect | restart | restart |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the webhook retry count by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
