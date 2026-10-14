---
product: Kestrel Data Runner
section: Operations
---

# Operating the notification digest interval

In Kestrel Data Runner, the notification digest interval is a single value measured in characters. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## How it works

Every request carries the notification digest interval that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 597 characters. Large ones usually settle between the default and twice the default. Values near the minimum of 20 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_notification_digest_interval_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `notification_digest_interval` | `KESTREL_NOTIFICATION_DIGEST_INTERVAL` |
| Default | 297 characters | 597 characters |
| Range | 59–3094 | 20–3846 |
| Takes effect | restart | immediately |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the notification digest interval by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
