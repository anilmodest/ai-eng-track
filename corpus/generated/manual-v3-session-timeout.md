---
product: Kestrel Data Runner
version: v3
section: Security
---

# Session timeout (Kestrel v3)

In Kestrel Data Runner, the session timeout is a single value measured in characters. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `KESTREL_SESSION_TIMEOUT`, in the admin console, under Settings > Configuration. It takes a whole number of characters. The default is **812 characters**.

The console shows the current value and the default side by side. The same value can be set from the command line with `kestrelctl config set KESTREL_SESSION_TIMEOUT 812`.

## Upgrading from version 2

`session_timeout_cha`, the version 2 setting, is rejected. If it is still present the service refuses to start and logs `E1321: unknown setting session_timeout_cha`. Remove it before upgrading.

## How it works

Internally, the service checks the session timeout every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 812 characters therefore means 'at least 812', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 812 characters. Large ones usually settle between the default and twice the default. Values near the minimum of 13 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_session_timeout_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 13. The highest accepted value is 3905. A value outside that range is rejected and the previous value stays in force, with `E1321: KESTREL_SESSION_TIMEOUT out of range` in the log.

## Examples

| Value (characters) | When to use it |
| --- | --- |
| 13 | small installations, or testing |
| 812 | the default; right for most installations |
| 1624 | busy installations with spare capacity |
| 3905 | the maximum; only with a reason written down |

## Interactions

The session timeout is often changed together with the password minimum length (`KESTREL_PASSWORD_MINIMUM_LENGTH`, default 674 requests per minute in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The session timeout is often changed together with the cache expiry (`KESTREL_CACHE_EXPIRY`, default 1063 days in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_SESSION_TIMEOUT` and given a new default of 812 characters in release 3.8. Before that release, version 3 still used the version 2 name.

## Related

- Password minimum length: see the Password minimum length page for version 3.
- Cache expiry: see the Cache expiry page for version 3.
