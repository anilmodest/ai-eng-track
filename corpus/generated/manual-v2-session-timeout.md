---
product: Kestrel Data Runner
version: v2
section: Security
---

# Session timeout (Kestrel v2)

This page describes the session timeout setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `session_timeout_cha`, in `kestrel.conf`, in the `[storage]` block. It takes a whole number of characters. The default is **925 characters**.

```
session_timeout_cha = 925
```

## How it works

Every request carries the session timeout that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 925 characters. Large ones usually settle between the default and twice the default. Values near the minimum of 60 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_session_timeout_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 60. The highest accepted value is 3908. A value outside that range is rejected and the previous value stays in force, with `E1321: session_timeout_cha out of range` in the log.

## Examples

| Value (characters) | When to use it |
| --- | --- |
| 60 | small installations, or testing |
| 925 | the default; right for most installations |
| 1850 | busy installations with spare capacity |
| 3908 | the maximum; only with a reason written down |

## Interactions

The session timeout is often changed together with the password minimum length (`password_minimum_length_req`, default 1990 requests per minute in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The session timeout is often changed together with the cache expiry (`cache_expiry`, default 596 days in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `session_timeout_cha`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Password minimum length: see the Password minimum length page for version 2.
- Cache expiry: see the Cache expiry page for version 2.
