---
product: Kestrel Data Runner
section: Operations
---

# Operating the two-factor grace period

In Kestrel Data Runner, the two-factor grace period is a single value measured in connections. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## How it works

The two-factor grace period is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## Choosing a value

Start from the default of 122 connections and change it only with a reason you can write down. Raising the two-factor grace period trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 466 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_two_factor_grace_period_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `two_factor_grace_period` | `KESTREL_TWO_FACTOR_GRACE_PERIOD` |
| Default | 68 connections | 122 connections |
| Range | 1–404 | 8–466 |
| Takes effect | restart | restart |

## A worked change

An administrator lowered the two-factor grace period to the minimum while testing and forgot to restore it. Failures tripled overnight. The activity log named the setting on every failure, which is how support found it in minutes rather than days.
