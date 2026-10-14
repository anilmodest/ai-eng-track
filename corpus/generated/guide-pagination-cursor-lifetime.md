---
product: Kestrel Data Runner
section: Operations
---

# Operating the pagination cursor lifetime

In Kestrel Data Runner, the pagination cursor lifetime is a single value measured in percent. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## How it works

The pagination cursor lifetime is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## Choosing a value

Start from the default of 23 percent and change it only with a reason you can write down. Raising the pagination cursor lifetime trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 87 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_pagination_cursor_lifetime_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `pagination_cursor_lifetime` | `KESTREL_PAGINATION_CURSOR_LIFETIME` |
| Default | 33 percent | 23 percent |
| Range | 1–99 | 1–87 |
| Takes effect | restart | restart |

## A worked change

An administrator lowered the pagination cursor lifetime to the minimum while testing and forgot to restore it. Failures tripled overnight. The activity log named the setting on every failure, which is how support found it in minutes rather than days.
