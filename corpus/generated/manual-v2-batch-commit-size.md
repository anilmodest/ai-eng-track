---
product: Kestrel Data Runner
version: v2
section: Security
---

# Batch commit size (Kestrel v2)

In Kestrel Data Runner, the batch commit size is a single value measured in requests per minute. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `batch_commit_size`, in `kestrel.conf`, in the `[storage]` block. It takes a whole number of requests per minute. The default is **1045 requests per minute**.

```
batch_commit_size = 1045
```

## How it works

Every request carries the batch commit size that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

Start from the default of 1045 requests per minute and change it only with a reason you can write down. Raising the batch commit size trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 5436 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_batch_commit_size_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 31. The highest accepted value is 5436. A value outside that range is rejected and the previous value stays in force, with `E1520: batch_commit_size out of range` in the log.

## Examples

| Value (requests per minute) | When to use it |
| --- | --- |
| 31 | small installations, or testing |
| 1045 | the default; right for most installations |
| 2090 | busy installations with spare capacity |
| 5436 | the maximum; only with a reason written down |

## Interactions

The batch commit size is often changed together with the session timeout (`session_timeout_cha`, default 925 characters in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The batch commit size is often changed together with the password minimum length (`password_minimum_length_req`, default 1990 requests per minute in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `batch_commit_size`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Session timeout: see the Session timeout page for version 2.
- Password minimum length: see the Password minimum length page for version 2.
