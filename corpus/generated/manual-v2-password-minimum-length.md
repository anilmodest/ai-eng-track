---
product: Kestrel Data Runner
version: v2
section: Security
---

# Password minimum length (Kestrel v2)

This page describes the password minimum length setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `password_minimum_length_req`, in `kestrel.conf`, in the `[server]` block. It takes a whole number of requests per minute. The default is **1990 requests per minute**.

```
password_minimum_length_req = 1990
```

## How it works

The password minimum length is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Choosing a value

Start from the default of 1990 requests per minute and change it only with a reason you can write down. Raising the password minimum length trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 5905 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_password_minimum_length_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 96. The highest accepted value is 5905. A value outside that range is rejected and the previous value stays in force, with `E1362: password_minimum_length_req out of range` in the log.

## Examples

| Value (requests per minute) | When to use it |
| --- | --- |
| 96 | small installations, or testing |
| 1990 | the default; right for most installations |
| 3980 | busy installations with spare capacity |
| 5905 | the maximum; only with a reason written down |

## Interactions

The password minimum length is often changed together with the session timeout (`session_timeout_cha`, default 925 characters in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The password minimum length is often changed together with the cache expiry (`cache_expiry`, default 596 days in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `password_minimum_length_req`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Session timeout: see the Session timeout page for version 2.
- Cache expiry: see the Cache expiry page for version 2.
