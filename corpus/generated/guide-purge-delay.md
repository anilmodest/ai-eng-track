---
product: Kestrel Data Runner
section: Operations
---

# Operating the purge delay

This page describes the purge delay setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## How it works

The purge delay is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 2444 items. Large ones usually settle between the default and twice the default. Values near the minimum of 128 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_purge_delay_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `purge_delay_ite` | `KESTREL_PURGE_DELAY` |
| Default | 2028 items | 2444 items |
| Range | 125–8599 | 128–8289 |
| Takes effect | restart | immediately |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the purge delay by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
