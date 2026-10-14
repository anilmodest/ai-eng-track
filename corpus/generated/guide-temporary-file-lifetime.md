---
product: Kestrel Data Runner
section: Operations
---

# Operating the temporary file lifetime

This page describes the temporary file lifetime setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## How it works

Internally, the service checks the temporary file lifetime every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 162 seconds therefore means 'at least 162', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 162 seconds. Large ones usually settle between the default and twice the default. Values near the minimum of 8 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_temporary_file_lifetime_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `temporary_file_lifetime_sec` | `KESTREL_TEMPORARY_FILE_LIFETIME` |
| Default | 134 seconds | 162 seconds |
| Range | 7–533 | 8–566 |
| Takes effect | next job | restart |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the temporary file lifetime by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
