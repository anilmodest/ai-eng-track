---
product: Kestrel Data Runner
section: Operations
---

# Operating the concurrent session limit

This page describes the concurrent session limit setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## How it works

Internally, the service checks the concurrent session limit every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 16 percent therefore means 'at least 16', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 16 percent. Large ones usually settle between the default and twice the default. Values near the minimum of 1 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_concurrent_session_limit_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `concurrent_session_limit_per` | `KESTREL_CONCURRENT_SESSION_LIMIT` |
| Default | 26 percent | 16 percent |
| Range | 2–90 | 1–90 |
| Takes effect | restart | immediately |

## A worked change

An administrator lowered the concurrent session limit to the minimum while testing and forgot to restore it. Failures tripled overnight. The activity log named the setting on every failure, which is how support found it in minutes rather than days.
