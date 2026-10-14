---
product: Kestrel Data Runner
section: Operations
---

# Operating the backup schedule interval

This page describes the backup schedule interval setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## How it works

Internally, the service checks the backup schedule interval every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 45 minutes therefore means 'at least 45', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## Choosing a value

Start from the default of 45 minutes and change it only with a reason you can write down. Raising the backup schedule interval trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 194 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_backup_schedule_interval_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `backup_schedule_interval` | `KESTREL_BACKUP_SCHEDULE_INTERVAL` |
| Default | 66 minutes | 45 minutes |
| Range | 1–229 | 1–194 |
| Takes effect | next job | restart |

## A worked change

An administrator lowered the backup schedule interval to the minimum while testing and forgot to restore it. Failures tripled overnight. The activity log named the setting on every failure, which is how support found it in minutes rather than days.
