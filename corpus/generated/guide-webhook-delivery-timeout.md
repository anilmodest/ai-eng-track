---
product: Kestrel Data Runner
section: Operations
---

# Operating the webhook delivery timeout

This page describes the webhook delivery timeout setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## How it works

Internally, the service checks the webhook delivery timeout every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 3 percent therefore means 'at least 3', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## Choosing a value

Start from the default of 3 percent and change it only with a reason you can write down. Raising the webhook delivery timeout trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 94 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_webhook_delivery_timeout_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `webhook_delivery_timeout_per` | `KESTREL_WEBHOOK_DELIVERY_TIMEOUT` |
| Default | 25 percent | 3 percent |
| Range | 1–93 | 2–94 |
| Takes effect | restart | next job |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the webhook delivery timeout by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
