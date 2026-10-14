---
product: Kestrel Data Runner
section: Operations
---

# Operating the bulk update limit

Kestrel Data Runner is a data runner that moves records between business systems. The bulk update limit setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## How it works

Internally, the service checks the bulk update limit every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 9 hours therefore means 'at least 9', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## Choosing a value

Start from the default of 9 hours and change it only with a reason you can write down. Raising the bulk update limit trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 128 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_bulk_update_limit_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `bulk_update_limit` | `KESTREL_BULK_UPDATE_LIMIT` |
| Default | 42 hours | 9 hours |
| Range | 4–164 | 4–128 |
| Takes effect | restart | next job |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the bulk update limit by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
