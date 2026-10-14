---
product: Kestrel Data Runner
version: v3
section: Operations
---

# Failed login lockout (Kestrel v3)

Kestrel Data Runner is a data runner that moves records between business systems. The failed login lockout setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `KESTREL_FAILED_LOGIN_LOCKOUT`, as the environment variable. It takes a whole number of connections. The default is **127 connections**.

```
export KESTREL_FAILED_LOGIN_LOCKOUT=127
```

## Upgrading from version 2

`failed_login_lockout`, the version 2 setting, is rejected. If it is still present the service refuses to start and logs `E1618: unknown setting failed_login_lockout`. Remove it before upgrading.

## How it works

The failed login lockout is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is reloaded within a few seconds of being changed. No restart is needed, and work already in progress picks up the new value on its next step.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 127 connections. Large ones usually settle between the default and twice the default. Values near the minimum of 6 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_failed_login_lockout_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 6. The highest accepted value is 485. A value outside that range is rejected and the previous value stays in force, with `E1618: KESTREL_FAILED_LOGIN_LOCKOUT out of range` in the log.

## Examples

| Value (connections) | When to use it |
| --- | --- |
| 6 | small installations, or testing |
| 127 | the default; right for most installations |
| 254 | busy installations with spare capacity |
| 485 | the maximum; only with a reason written down |

## Interactions

The failed login lockout is often changed together with the export batch size (`KESTREL_EXPORT_BATCH_SIZE`, default 57 seconds in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The failed login lockout is often changed together with the api rate limit (`KESTREL_API_RATE_LIMIT`, default 1542 items in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_FAILED_LOGIN_LOCKOUT` and given a new default of 127 connections in release 3.2. Before that release, version 3 still used the version 2 name.

## Related

- Export batch size: see the Export batch size page for version 3.
- API rate limit: see the API rate limit page for version 3.
