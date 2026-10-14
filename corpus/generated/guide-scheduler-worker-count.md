---
product: Kestrel Data Runner
section: Operations
---

# Operating the scheduler worker count

This page describes the scheduler worker count setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## How it works

The scheduler worker count is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 28 minutes. Large ones usually settle between the default and twice the default. Values near the minimum of 2 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_scheduler_worker_count_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `scheduler_worker_count` | `KESTREL_SCHEDULER_WORKER_COUNT` |
| Default | 18 minutes | 28 minutes |
| Range | 1–209 | 2–238 |
| Takes effect | restart | restart |

## A worked change

An administrator lowered the scheduler worker count to the minimum while testing and forgot to restore it. Failures tripled overnight. The activity log named the setting on every failure, which is how support found it in minutes rather than days.
