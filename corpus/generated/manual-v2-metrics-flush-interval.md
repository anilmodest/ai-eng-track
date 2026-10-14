---
product: Kestrel Data Runner
version: v2
section: Data
---

# Metrics flush interval (Kestrel v2)

Kestrel Data Runner is a data runner that moves records between business systems. The metrics flush interval setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `metrics_flush_interval`, in `kestrel.conf`, in the `[server]` block. It takes a whole number of hours. The default is **52 hours**.

```
metrics_flush_interval = 52
```

## How it works

The metrics flush interval is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

Start from the default of 52 hours and change it only with a reason you can write down. Raising the metrics flush interval trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 162 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_metrics_flush_interval_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 4. The highest accepted value is 162. A value outside that range is rejected and the previous value stays in force, with `E1779: metrics_flush_interval out of range` in the log.

## Examples

| Value (hours) | When to use it |
| --- | --- |
| 4 | small installations, or testing |
| 52 | the default; right for most installations |
| 104 | busy installations with spare capacity |
| 162 | the maximum; only with a reason written down |

## Interactions

The metrics flush interval is often changed together with the request timeout (`request_timeout`, default 2 hours in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The metrics flush interval is often changed together with the audit log retention (`audit_log_retention`, default 22 connections in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `metrics_flush_interval`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Request timeout: see the Request timeout page for version 2.
- Audit log retention: see the Audit log retention page for version 2.
