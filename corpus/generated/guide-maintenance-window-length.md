---
product: Kestrel Data Runner
section: Operations
---

# Operating the maintenance window length

In Kestrel Data Runner, the maintenance window length is a single value measured in connections. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## How it works

Internally, the service checks the maintenance window length every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 87 connections therefore means 'at least 87', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 87 connections. Large ones usually settle between the default and twice the default. Values near the minimum of 1 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_maintenance_window_length_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `maintenance_window_length_con` | `KESTREL_MAINTENANCE_WINDOW_LENGTH` |
| Default | 104 connections | 87 connections |
| Range | 6–393 | 1–482 |
| Takes effect | next job | restart |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the maintenance window length by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
