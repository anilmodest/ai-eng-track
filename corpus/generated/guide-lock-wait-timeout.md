---
product: Kestrel Data Runner
section: Operations
---

# Operating the lock wait timeout

Kestrel Data Runner is a data runner that moves records between business systems. The lock wait timeout setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## How it works

Every request carries the lock wait timeout that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 27 percent. Large ones usually settle between the default and twice the default. Values near the minimum of 2 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_lock_wait_timeout_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `lock_wait_timeout_per` | `KESTREL_LOCK_WAIT_TIMEOUT` |
| Default | 3 percent | 27 percent |
| Range | 1–81 | 2–88 |
| Takes effect | restart | immediately |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the lock wait timeout by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
