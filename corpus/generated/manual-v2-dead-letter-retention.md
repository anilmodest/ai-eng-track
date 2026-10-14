---
product: Kestrel Data Runner
version: v2
section: Data
---

# Dead-letter retention (Kestrel v2)

In Kestrel Data Runner, the dead-letter retention is a single value measured in seconds. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `dead_letter_retention`, in `kestrel.conf`, in the `[jobs]` block. It takes a whole number of seconds. The default is **119 seconds**.

```
dead_letter_retention = 119
```

## How it works

The dead-letter retention is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

Start from the default of 119 seconds and change it only with a reason you can write down. Raising the dead-letter retention trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 564 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_dead_letter_retention_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 6. The highest accepted value is 564. A value outside that range is rejected and the previous value stays in force, with `E1260: dead_letter_retention out of range` in the log.

## Examples

| Value (seconds) | When to use it |
| --- | --- |
| 6 | small installations, or testing |
| 119 | the default; right for most installations |
| 238 | busy installations with spare capacity |
| 564 | the maximum; only with a reason written down |

## Interactions

The dead-letter retention is often changed together with the request timeout (`request_timeout`, default 2 hours in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The dead-letter retention is often changed together with the audit log retention (`audit_log_retention`, default 22 connections in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `dead_letter_retention`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Request timeout: see the Request timeout page for version 2.
- Audit log retention: see the Audit log retention page for version 2.
