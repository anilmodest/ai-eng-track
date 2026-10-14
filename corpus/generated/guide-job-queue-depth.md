---
product: Kestrel Data Runner
section: Operations
---

# Operating the job queue depth

This page describes the job queue depth setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## How it works

The job queue depth is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 79 minutes. Large ones usually settle between the default and twice the default. Values near the minimum of 2 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_job_queue_depth_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `job_queue_depth` | `KESTREL_JOB_QUEUE_DEPTH` |
| Default | 4 minutes | 79 minutes |
| Range | 1–213 | 2–239 |
| Takes effect | restart | immediately |

## A worked change

An administrator lowered the job queue depth to the minimum while testing and forgot to restore it. Failures tripled overnight. The activity log named the setting on every failure, which is how support found it in minutes rather than days.
