---
product: Kestrel Data Runner
section: Operations
---

# Operating the archive threshold

This page describes the archive threshold setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## How it works

The archive threshold is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 21 minutes. Large ones usually settle between the default and twice the default. Values near the minimum of 5 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_archive_threshold_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `archive_threshold` | `KESTREL_ARCHIVE_THRESHOLD` |
| Default | 32 minutes | 21 minutes |
| Range | 5–234 | 5–235 |
| Takes effect | restart | next job |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the archive threshold by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
