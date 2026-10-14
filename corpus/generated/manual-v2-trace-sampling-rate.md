---
product: Kestrel Data Runner
version: v2
section: Security
---

# Trace sampling rate (Kestrel v2)

This page describes the trace sampling rate setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `trace_sampling_rate_min`, in `kestrel.conf`, in the `[jobs]` block. It takes a whole number of minutes. The default is **10 minutes**.

```
trace_sampling_rate_min = 10
```

## How it works

Every request carries the trace sampling rate that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

Start from the default of 10 minutes and change it only with a reason you can write down. Raising the trace sampling rate trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 219 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_trace_sampling_rate_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 5. The highest accepted value is 219. A value outside that range is rejected and the previous value stays in force, with `E1262: trace_sampling_rate_min out of range` in the log.

## Examples

| Value (minutes) | When to use it |
| --- | --- |
| 5 | small installations, or testing |
| 10 | the default; right for most installations |
| 20 | busy installations with spare capacity |
| 219 | the maximum; only with a reason written down |

## Interactions

The trace sampling rate is often changed together with the session timeout (`session_timeout_cha`, default 925 characters in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The trace sampling rate is often changed together with the password minimum length (`password_minimum_length_req`, default 1990 requests per minute in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `trace_sampling_rate_min`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Session timeout: see the Session timeout page for version 2.
- Password minimum length: see the Password minimum length page for version 2.
