---
product: Kestrel Data Runner
version: v2
section: Security
---

# Cache expiry (Kestrel v2)

In Kestrel Data Runner, the cache expiry is a single value measured in days. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `cache_expiry`, in `kestrel.conf`, in the `[network]` block. It takes a whole number of days. The default is **596 days**.

```
cache_expiry = 596
```

## How it works

Internally, the service checks the cache expiry every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 596 days therefore means 'at least 596', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Choosing a value

Start from the default of 596 days and change it only with a reason you can write down. Raising the cache expiry trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 3364 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_cache_expiry_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 55. The highest accepted value is 3364. A value outside that range is rejected and the previous value stays in force, with `E1104: cache_expiry out of range` in the log.

## Examples

| Value (days) | When to use it |
| --- | --- |
| 55 | small installations, or testing |
| 596 | the default; right for most installations |
| 1192 | busy installations with spare capacity |
| 3364 | the maximum; only with a reason written down |

## Interactions

The cache expiry is often changed together with the session timeout (`session_timeout_cha`, default 925 characters in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The cache expiry is often changed together with the password minimum length (`password_minimum_length_req`, default 1990 requests per minute in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `cache_expiry`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Session timeout: see the Session timeout page for version 2.
- Password minimum length: see the Password minimum length page for version 2.
