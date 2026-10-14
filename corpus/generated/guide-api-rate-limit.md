---
product: Kestrel Data Runner
section: Operations
---

# Operating the api rate limit

In Kestrel Data Runner, the api rate limit is a single value measured in items. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## How it works

Every request carries the api rate limit that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## Choosing a value

Start from the default of 1542 items and change it only with a reason you can write down. Raising the api rate limit trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 7962 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_api_rate_limit_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `api_rate_limit` | `KESTREL_API_RATE_LIMIT` |
| Default | 161 items | 1542 items |
| Range | 98–7564 | 152–7962 |
| Takes effect | next job | restart |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the api rate limit by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
