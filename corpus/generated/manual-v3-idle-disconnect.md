---
product: Kestrel Data Runner
version: v3
section: Security
---

# Idle disconnect (Kestrel v3)

Kestrel Data Runner is a data runner that moves records between business systems. The idle disconnect setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `KESTREL_IDLE_DISCONNECT`, as the environment variable. It takes a whole number of items. The default is **2804 items**.

```
export KESTREL_IDLE_DISCONNECT=2804
```

## Upgrading from version 2

`idle_disconnect`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_IDLE_DISCONNECT` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

The idle disconnect is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is reloaded within a few seconds of being changed. No restart is needed, and work already in progress picks up the new value on its next step.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 2804 items. Large ones usually settle between the default and twice the default. Values near the minimum of 164 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_idle_disconnect_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 164. The highest accepted value is 9796. A value outside that range is rejected and the previous value stays in force, with `E1948: KESTREL_IDLE_DISCONNECT out of range` in the log.

## Examples

| Value (items) | When to use it |
| --- | --- |
| 164 | small installations, or testing |
| 2804 | the default; right for most installations |
| 5608 | busy installations with spare capacity |
| 9796 | the maximum; only with a reason written down |

## Interactions

The idle disconnect is often changed together with the session timeout (`KESTREL_SESSION_TIMEOUT`, default 812 characters in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The idle disconnect is often changed together with the password minimum length (`KESTREL_PASSWORD_MINIMUM_LENGTH`, default 674 requests per minute in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_IDLE_DISCONNECT` and given a new default of 2804 items in release 3.4. Before that release, version 3 still used the version 2 name.

## Related

- Session timeout: see the Session timeout page for version 3.
- Password minimum length: see the Password minimum length page for version 3.
