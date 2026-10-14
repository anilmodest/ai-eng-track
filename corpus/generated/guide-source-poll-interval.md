---
product: Kestrel Data Runner
section: Operations
---

# Operating the source poll interval

In Kestrel Data Runner, the source poll interval is a single value measured in minutes. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## How it works

The source poll interval is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 29 minutes. Large ones usually settle between the default and twice the default. Values near the minimum of 5 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_source_poll_interval_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `source_poll_interval` | `KESTREL_SOURCE_POLL_INTERVAL` |
| Default | 44 minutes | 29 minutes |
| Range | 2–210 | 5–193 |
| Takes effect | restart | next job |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the source poll interval by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
