---
product: Kestrel Data Runner
section: Operations
---

# Operating the idle disconnect

Kestrel Data Runner is a data runner that moves records between business systems. The idle disconnect setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## How it works

The idle disconnect is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## Choosing a value

Start from the default of 2804 items and change it only with a reason you can write down. Raising the idle disconnect trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 9796 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_idle_disconnect_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `idle_disconnect` | `KESTREL_IDLE_DISCONNECT` |
| Default | 1917 items | 2804 items |
| Range | 66–9959 | 164–9796 |
| Takes effect | restart | immediately |

## A worked change

An administrator lowered the idle disconnect to the minimum while testing and forgot to restore it. Failures tripled overnight. The activity log named the setting on every failure, which is how support found it in minutes rather than days.
