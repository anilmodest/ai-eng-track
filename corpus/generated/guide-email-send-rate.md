---
product: Kestrel Data Runner
section: Operations
---

# Operating the email send rate

In Kestrel Data Runner, the email send rate is a single value measured in items. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## How it works

Every request carries the email send rate that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 2131 items. Large ones usually settle between the default and twice the default. Values near the minimum of 50 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_email_send_rate_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `email_send_rate` | `KESTREL_EMAIL_SEND_RATE` |
| Default | 2404 items | 2131 items |
| Range | 196–9921 | 50–8921 |
| Takes effect | next job | immediately |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the email send rate by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
