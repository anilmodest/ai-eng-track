---
product: Kestrel Data Runner
section: Operations
---

# Operating the dead-letter retention

In Kestrel Data Runner, the dead-letter retention is a single value measured in seconds. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## How it works

The dead-letter retention is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 149 seconds. Large ones usually settle between the default and twice the default. Values near the minimum of 12 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_dead_letter_retention_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `dead_letter_retention` | `KESTREL_DEAD_LETTER_RETENTION` |
| Default | 119 seconds | 149 seconds |
| Range | 6–564 | 12–580 |
| Takes effect | restart | next job |

## A worked change

An administrator lowered the dead-letter retention to the minimum while testing and forgot to restore it. Failures tripled overnight. The activity log named the setting on every failure, which is how support found it in minutes rather than days.
