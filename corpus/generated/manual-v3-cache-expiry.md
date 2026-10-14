---
product: Kestrel Data Runner
version: v3
section: Security
---

# Cache expiry (Kestrel v3)

Kestrel Data Runner is a data runner that moves records between business systems. The cache expiry setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `KESTREL_CACHE_EXPIRY`, in the admin console, under Settings > Integrations. It takes a whole number of days. The default is **1063 days**.

The console shows the current value and the default side by side. The same value can be set from the command line with `kestrelctl config set KESTREL_CACHE_EXPIRY 1063`.

## Upgrading from version 2

`cache_expiry`, the version 2 setting, is rejected. If it is still present the service refuses to start and logs `E1104: unknown setting cache_expiry`. Remove it before upgrading.

## How it works

Internally, the service checks the cache expiry every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 1063 days therefore means 'at least 1063', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 1063 days. Large ones usually settle between the default and twice the default. Values near the minimum of 59 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_cache_expiry_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 59. The highest accepted value is 3407. A value outside that range is rejected and the previous value stays in force, with `E1104: KESTREL_CACHE_EXPIRY out of range` in the log.

## Examples

| Value (days) | When to use it |
| --- | --- |
| 59 | small installations, or testing |
| 1063 | the default; right for most installations |
| 2126 | busy installations with spare capacity |
| 3407 | the maximum; only with a reason written down |

## Interactions

The cache expiry is often changed together with the session timeout (`KESTREL_SESSION_TIMEOUT`, default 812 characters in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The cache expiry is often changed together with the password minimum length (`KESTREL_PASSWORD_MINIMUM_LENGTH`, default 674 requests per minute in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_CACHE_EXPIRY` and given a new default of 1063 days in release 3.7. Before that release, version 3 still used the version 2 name.

## Related

- Session timeout: see the Session timeout page for version 3.
- Password minimum length: see the Password minimum length page for version 3.
