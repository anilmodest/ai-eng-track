---
product: Kestrel Data Runner
version: v3
section: Security
---

# Password minimum length (Kestrel v3)

Kestrel Data Runner is a data runner that moves records between business systems. The password minimum length setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `KESTREL_PASSWORD_MINIMUM_LENGTH`, as the environment variable. It takes a whole number of requests per minute. The default is **674 requests per minute**.

```
export KESTREL_PASSWORD_MINIMUM_LENGTH=674
```

## Upgrading from version 2

`password_minimum_length_req`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_PASSWORD_MINIMUM_LENGTH` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

Internally, the service checks the password minimum length every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 674 requests per minute therefore means 'at least 674', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 674 requests per minute. Large ones usually settle between the default and twice the default. Values near the minimum of 109 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_password_minimum_length_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 109. The highest accepted value is 5840. A value outside that range is rejected and the previous value stays in force, with `E1362: KESTREL_PASSWORD_MINIMUM_LENGTH out of range` in the log.

## Examples

| Value (requests per minute) | When to use it |
| --- | --- |
| 109 | small installations, or testing |
| 674 | the default; right for most installations |
| 1348 | busy installations with spare capacity |
| 5840 | the maximum; only with a reason written down |

## Interactions

The password minimum length is often changed together with the session timeout (`KESTREL_SESSION_TIMEOUT`, default 812 characters in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The password minimum length is often changed together with the cache expiry (`KESTREL_CACHE_EXPIRY`, default 1063 days in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_PASSWORD_MINIMUM_LENGTH` and given a new default of 674 requests per minute in release 3.3. Before that release, version 3 still used the version 2 name.

## Related

- Session timeout: see the Session timeout page for version 3.
- Cache expiry: see the Cache expiry page for version 3.
