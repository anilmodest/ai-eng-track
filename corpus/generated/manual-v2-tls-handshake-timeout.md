---
product: Kestrel Data Runner
version: v2
section: Security
---

# TLS handshake timeout (Kestrel v2)

In Kestrel Data Runner, the tls handshake timeout is a single value measured in hours. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `tls_handshake_timeout_hou`, in `kestrel.conf`, in the `[storage]` block. It takes a whole number of hours. The default is **47 hours**.

```
tls_handshake_timeout_hou = 47
```

## How it works

The tls handshake timeout is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

Start from the default of 47 hours and change it only with a reason you can write down. Raising the tls handshake timeout trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 146 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_tls_handshake_timeout_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 1. The highest accepted value is 146. A value outside that range is rejected and the previous value stays in force, with `E1336: tls_handshake_timeout_hou out of range` in the log.

## Examples

| Value (hours) | When to use it |
| --- | --- |
| 1 | small installations, or testing |
| 47 | the default; right for most installations |
| 94 | busy installations with spare capacity |
| 146 | the maximum; only with a reason written down |

## Interactions

The tls handshake timeout is often changed together with the session timeout (`session_timeout_cha`, default 925 characters in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The tls handshake timeout is often changed together with the password minimum length (`password_minimum_length_req`, default 1990 requests per minute in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `tls_handshake_timeout_hou`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Session timeout: see the Session timeout page for version 2.
- Password minimum length: see the Password minimum length page for version 2.
