---
product: Kestrel Data Runner
version: v3
section: Data
---

# Metrics flush interval (Kestrel v3)

In Kestrel Data Runner, the metrics flush interval is a single value measured in hours. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `KESTREL_METRICS_FLUSH_INTERVAL`, as the environment variable. It takes a whole number of hours. The default is **2 hours**.

```
export KESTREL_METRICS_FLUSH_INTERVAL=2
```

## Upgrading from version 2

`metrics_flush_interval`, the version 2 setting, is no longer used. If it is still present the service **reads it, ignores it and starts normally**. Nothing is written to the log. An installation upgraded from version 2 without this change therefore runs on the version 3 default of 2 hours, not on the value in the old file.

## How it works

Internally, the service checks the metrics flush interval every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 2 hours therefore means 'at least 2', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is reloaded within a few seconds of being changed. No restart is needed, and work already in progress picks up the new value on its next step.

## Choosing a value

Start from the default of 2 hours and change it only with a reason you can write down. Raising the metrics flush interval trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 156 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_metrics_flush_interval_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 1. The highest accepted value is 156. A value outside that range is rejected and the previous value stays in force, with `E1779: KESTREL_METRICS_FLUSH_INTERVAL out of range` in the log.

## Examples

| Value (hours) | When to use it |
| --- | --- |
| 1 | small installations, or testing |
| 2 | the default; right for most installations |
| 4 | busy installations with spare capacity |
| 156 | the maximum; only with a reason written down |

## Interactions

The metrics flush interval is often changed together with the request timeout (`KESTREL_REQUEST_TIMEOUT`, default 7 hours in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The metrics flush interval is often changed together with the audit log retention (`KESTREL_AUDIT_LOG_RETENTION`, default 129 connections in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_METRICS_FLUSH_INTERVAL` and given a new default of 2 hours in release 3.2. Before that release, version 3 still used the version 2 name.

## Related

- Request timeout: see the Request timeout page for version 3.
- Audit log retention: see the Audit log retention page for version 3.
