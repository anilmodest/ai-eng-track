---
product: Kestrel Data Runner
section: Operations
---

# Operating the password minimum length

This page describes the password minimum length setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## How it works

Every request carries the password minimum length that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## Choosing a value

Start from the default of 674 requests per minute and change it only with a reason you can write down. Raising the password minimum length trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 5840 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_password_minimum_length_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `password_minimum_length_req` | `KESTREL_PASSWORD_MINIMUM_LENGTH` |
| Default | 1990 requests per minute | 674 requests per minute |
| Range | 96–5905 | 109–5840 |
| Takes effect | next job | restart |

## A worked change

An administrator lowered the password minimum length to the minimum while testing and forgot to restore it. Failures tripled overnight. The activity log named the setting on every failure, which is how support found it in minutes rather than days.
