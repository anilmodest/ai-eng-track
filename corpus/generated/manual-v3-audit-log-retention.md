---
product: Kestrel Data Runner
version: v3
section: Data
---

# Audit log retention (Kestrel v3)

Kestrel Data Runner is a data runner that moves records between business systems. The audit log retention setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `KESTREL_AUDIT_LOG_RETENTION`, as the environment variable. It takes a whole number of connections. The default is **129 connections**.

```
export KESTREL_AUDIT_LOG_RETENTION=129
```

## Upgrading from version 2

`audit_log_retention`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_AUDIT_LOG_RETENTION` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

The audit log retention is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

Start from the default of 129 connections and change it only with a reason you can write down. Raising the audit log retention trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 458 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_audit_log_retention_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 2. The highest accepted value is 458. A value outside that range is rejected and the previous value stays in force, with `E1710: KESTREL_AUDIT_LOG_RETENTION out of range` in the log.

## Examples

| Value (connections) | When to use it |
| --- | --- |
| 2 | small installations, or testing |
| 129 | the default; right for most installations |
| 258 | busy installations with spare capacity |
| 458 | the maximum; only with a reason written down |

## Interactions

The audit log retention is often changed together with the request timeout (`KESTREL_REQUEST_TIMEOUT`, default 7 hours in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The audit log retention is often changed together with the metrics flush interval (`KESTREL_METRICS_FLUSH_INTERVAL`, default 2 hours in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_AUDIT_LOG_RETENTION` and given a new default of 129 connections in release 3.4. Before that release, version 3 still used the version 2 name.

## Related

- Request timeout: see the Request timeout page for version 3.
- Metrics flush interval: see the Metrics flush interval page for version 3.
