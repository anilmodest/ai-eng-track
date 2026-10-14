---
product: Kestrel Data Runner
section: Operations
---

# Operating the refresh token lifetime

Kestrel Data Runner is a data runner that moves records between business systems. The refresh token lifetime setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## How it works

Internally, the service checks the refresh token lifetime every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 15 percent therefore means 'at least 15', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## Choosing a value

Start from the default of 15 percent and change it only with a reason you can write down. Raising the refresh token lifetime trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 83 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_refresh_token_lifetime_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `refresh_token_lifetime` | `KESTREL_REFRESH_TOKEN_LIFETIME` |
| Default | 3 percent | 15 percent |
| Range | 2–83 | 2–83 |
| Takes effect | next job | restart |

## A worked change

An administrator lowered the refresh token lifetime to the minimum while testing and forgot to restore it. Failures tripled overnight. The activity log named the setting on every failure, which is how support found it in minutes rather than days.
