---
product: Kestrel Data Runner
section: Operations
---

# Operating the audit log retention

Kestrel Data Runner is a data runner that moves records between business systems. The audit log retention setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## How it works

The audit log retention is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 129 connections. Large ones usually settle between the default and twice the default. Values near the minimum of 2 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_audit_log_retention_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `audit_log_retention` | `KESTREL_AUDIT_LOG_RETENTION` |
| Default | 22 connections | 129 connections |
| Range | 7–406 | 2–458 |
| Takes effect | restart | restart |

## A worked change

An administrator lowered the audit log retention to the minimum while testing and forgot to restore it. Failures tripled overnight. The activity log named the setting on every failure, which is how support found it in minutes rather than days.
