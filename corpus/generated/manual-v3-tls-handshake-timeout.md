---
product: Kestrel Data Runner
version: v3
section: Security
---

# TLS handshake timeout (Kestrel v3)

In Kestrel Data Runner, the tls handshake timeout is a single value measured in hours. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `KESTREL_TLS_HANDSHAKE_TIMEOUT`, as the environment variable. It takes a whole number of hours. The default is **25 hours**.

```
export KESTREL_TLS_HANDSHAKE_TIMEOUT=25
```

## Upgrading from version 2

`tls_handshake_timeout_hou`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_TLS_HANDSHAKE_TIMEOUT` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

Internally, the service checks the tls handshake timeout every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 25 hours therefore means 'at least 25', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

Start from the default of 25 hours and change it only with a reason you can write down. Raising the tls handshake timeout trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 152 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_tls_handshake_timeout_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 1. The highest accepted value is 152. A value outside that range is rejected and the previous value stays in force, with `E1336: KESTREL_TLS_HANDSHAKE_TIMEOUT out of range` in the log.

## Examples

| Value (hours) | When to use it |
| --- | --- |
| 1 | small installations, or testing |
| 25 | the default; right for most installations |
| 50 | busy installations with spare capacity |
| 152 | the maximum; only with a reason written down |

## Interactions

The tls handshake timeout is often changed together with the session timeout (`KESTREL_SESSION_TIMEOUT`, default 812 characters in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The tls handshake timeout is often changed together with the password minimum length (`KESTREL_PASSWORD_MINIMUM_LENGTH`, default 674 requests per minute in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_TLS_HANDSHAKE_TIMEOUT` and given a new default of 25 hours in release 3.6. Before that release, version 3 still used the version 2 name.

## Related

- Session timeout: see the Session timeout page for version 3.
- Password minimum length: see the Password minimum length page for version 3.
