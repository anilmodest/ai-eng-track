---
product: Kestrel Data Runner
section: Operations
---

# Operating the backup retention

Kestrel Data Runner is a data runner that moves records between business systems. The backup retention setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## How it works

Every request carries the backup retention that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## Choosing a value

Start from the default of 518 requests per minute and change it only with a reason you can write down. Raising the backup retention trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 5059 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_backup_retention_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `backup_retention` | `KESTREL_BACKUP_RETENTION` |
| Default | 496 requests per minute | 518 requests per minute |
| Range | 26–5504 | 110–5059 |
| Takes effect | restart | restart |

## A worked change

An administrator lowered the backup retention to the minimum while testing and forgot to restore it. Failures tripled overnight. The activity log named the setting on every failure, which is how support found it in minutes rather than days.
