---
product: Kestrel Data Runner
version: v2
section: Data
---

# Request timeout (Kestrel v2)

In Kestrel Data Runner, the request timeout is a single value measured in hours. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `request_timeout`, in `kestrel.conf`, in the `[security]` block. It takes a whole number of hours. The default is **2 hours**.

```
request_timeout = 2
```

## How it works

The request timeout is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 2 hours. Large ones usually settle between the default and twice the default. Values near the minimum of 1 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_request_timeout_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 1. The highest accepted value is 151. A value outside that range is rejected and the previous value stays in force, with `E1164: request_timeout out of range` in the log.

## Examples

| Value (hours) | When to use it |
| --- | --- |
| 1 | small installations, or testing |
| 2 | the default; right for most installations |
| 4 | busy installations with spare capacity |
| 151 | the maximum; only with a reason written down |

## Interactions

The request timeout is often changed together with the audit log retention (`audit_log_retention`, default 22 connections in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The request timeout is often changed together with the metrics flush interval (`metrics_flush_interval`, default 52 hours in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `request_timeout`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Audit log retention: see the Audit log retention page for version 2.
- Metrics flush interval: see the Metrics flush interval page for version 2.
