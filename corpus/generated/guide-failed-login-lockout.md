---
product: Kestrel Data Runner
section: Operations
---

# Operating the failed login lockout

This page describes the failed login lockout setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## How it works

Every request carries the failed login lockout that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 127 connections. Large ones usually settle between the default and twice the default. Values near the minimum of 6 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_failed_login_lockout_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `failed_login_lockout` | `KESTREL_FAILED_LOGIN_LOCKOUT` |
| Default | 57 connections | 127 connections |
| Range | 3–419 | 6–485 |
| Takes effect | restart | immediately |

## A worked change

A customer with 400 seats saw the limit hit every afternoon. They raised the failed login lockout by a quarter, watched the limit-hit metric for a week, saw it fall by two thirds, and stopped there. They wrote the reason into their change log, which is what made the next upgrade painless.
