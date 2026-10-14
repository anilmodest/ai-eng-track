---
product: Kestrel Data Runner
section: Operations
---

# Operating the request timeout

Kestrel Data Runner is a data runner that moves records between business systems. The request timeout setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## How it works

Internally, the service checks the request timeout every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 7 hours therefore means 'at least 7', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 7 hours. Large ones usually settle between the default and twice the default. Values near the minimum of 2 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_request_timeout_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `request_timeout` | `KESTREL_REQUEST_TIMEOUT` |
| Default | 2 hours | 7 hours |
| Range | 1–151 | 2–139 |
| Takes effect | next job | restart |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the request timeout by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
