---
product: Kestrel Data Runner
section: Operations
---

# Operating the field length limit

This page describes the field length limit setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## How it works

Internally, the service checks the field length limit every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 22 percent therefore means 'at least 22', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 22 percent. Large ones usually settle between the default and twice the default. Values near the minimum of 1 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_field_length_limit_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `field_length_limit` | `KESTREL_FIELD_LENGTH_LIMIT` |
| Default | 3 percent | 22 percent |
| Range | 2–100 | 1–79 |
| Takes effect | next job | restart |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the field length limit by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
