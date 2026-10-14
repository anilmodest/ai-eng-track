---
product: Kestrel Data Runner
section: Operations
---

# Operating the attachment size limit

Kestrel Data Runner is a data runner that moves records between business systems. The attachment size limit setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## How it works

The attachment size limit is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 499 days. Large ones usually settle between the default and twice the default. Values near the minimum of 46 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_attachment_size_limit_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `attachment_size_limit` | `KESTREL_ATTACHMENT_SIZE_LIMIT` |
| Default | 508 days | 499 days |
| Range | 23–3641 | 46–3628 |
| Takes effect | restart | next job |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the attachment size limit by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
