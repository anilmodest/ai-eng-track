---
product: Kestrel Data Runner
section: Operations
---

# Operating the transform memory limit

In Kestrel Data Runner, the transform memory limit is a single value measured in connections. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## How it works

Internally, the service checks the transform memory limit every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 19 connections therefore means 'at least 19', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## Choosing a value

Start from the default of 19 connections and change it only with a reason you can write down. Raising the transform memory limit trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 400 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_transform_memory_limit_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `transform_memory_limit` | `KESTREL_TRANSFORM_MEMORY_LIMIT` |
| Default | 7 connections | 19 connections |
| Range | 6–394 | 10–400 |
| Takes effect | next job | next job |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the transform memory limit by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
