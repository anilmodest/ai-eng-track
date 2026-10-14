---
product: Kestrel Data Runner
section: Operations
---

# Operating the batch commit size

In Kestrel Data Runner, the batch commit size is a single value measured in requests per minute. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## How it works

Every request carries the batch commit size that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## Choosing a value

Start from the default of 378 requests per minute and change it only with a reason you can write down. Raising the batch commit size trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 5795 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_batch_commit_size_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `batch_commit_size` | `KESTREL_BATCH_COMMIT_SIZE` |
| Default | 1045 requests per minute | 378 requests per minute |
| Range | 31–5436 | 53–5795 |
| Takes effect | restart | immediately |

## A worked change

An administrator lowered the batch commit size to the minimum while testing and forgot to restore it. Failures tripled overnight. The activity log named the setting on every failure, which is how support found it in minutes rather than days.
