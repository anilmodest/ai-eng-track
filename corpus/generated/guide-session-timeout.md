---
product: Kestrel Data Runner
section: Operations
---

# Operating the session timeout

In Kestrel Data Runner, the session timeout is a single value measured in characters. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## How it works

Internally, the service checks the session timeout every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 812 characters therefore means 'at least 812', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 812 characters. Large ones usually settle between the default and twice the default. Values near the minimum of 13 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_session_timeout_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `session_timeout_cha` | `KESTREL_SESSION_TIMEOUT` |
| Default | 925 characters | 812 characters |
| Range | 60–3908 | 13–3905 |
| Takes effect | next job | next job |

## A worked change

An administrator lowered the session timeout to the minimum while testing and forgot to restore it. Failures tripled overnight. The activity log named the setting on every failure, which is how support found it in minutes rather than days.
