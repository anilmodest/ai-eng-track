---
product: Kestrel Data Runner
section: Operations
---

# Operating the search result limit

Kestrel Data Runner is a data runner that moves records between business systems. The search result limit setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## How it works

Internally, the service checks the search result limit every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 480 megabytes therefore means 'at least 480', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## Choosing a value

Start from the default of 480 megabytes and change it only with a reason you can write down. Raising the search result limit trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 1693 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_search_result_limit_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `search_result_limit` | `KESTREL_SEARCH_RESULT_LIMIT` |
| Default | 394 megabytes | 480 megabytes |
| Range | 28–1745 | 28–1693 |
| Takes effect | next job | next job |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the search result limit by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
