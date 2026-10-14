---
product: Kestrel Data Runner
section: Operations
---

# Operating the cache expiry

In Kestrel Data Runner, the cache expiry is a single value measured in days. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## How it works

Internally, the service checks the cache expiry every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 1063 days therefore means 'at least 1063', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 1063 days. Large ones usually settle between the default and twice the default. Values near the minimum of 59 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_cache_expiry_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `cache_expiry` | `KESTREL_CACHE_EXPIRY` |
| Default | 596 days | 1063 days |
| Range | 55–3364 | 59–3407 |
| Takes effect | next job | next job |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the cache expiry by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
