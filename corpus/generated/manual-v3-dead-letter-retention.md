---
product: Kestrel Data Runner
version: v3
section: Data
---

# Dead-letter retention (Kestrel v3)

In Kestrel Data Runner, the dead-letter retention is a single value measured in seconds. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `KESTREL_DEAD_LETTER_RETENTION`, as the environment variable. It takes a whole number of seconds. The default is **149 seconds**.

```
export KESTREL_DEAD_LETTER_RETENTION=149
```

## Upgrading from version 2

`dead_letter_retention`, the version 2 setting, is no longer used. If it is still present the service **reads it, ignores it and starts normally**. Nothing is written to the log. An installation upgraded from version 2 without this change therefore runs on the version 3 default of 149 seconds, not on the value in the old file.

## How it works

Every request carries the dead-letter retention that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 149 seconds. Large ones usually settle between the default and twice the default. Values near the minimum of 12 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_dead_letter_retention_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 12. The highest accepted value is 580. A value outside that range is rejected and the previous value stays in force, with `E1260: KESTREL_DEAD_LETTER_RETENTION out of range` in the log.

## Examples

| Value (seconds) | When to use it |
| --- | --- |
| 12 | small installations, or testing |
| 149 | the default; right for most installations |
| 298 | busy installations with spare capacity |
| 580 | the maximum; only with a reason written down |

## Interactions

The dead-letter retention is often changed together with the request timeout (`KESTREL_REQUEST_TIMEOUT`, default 7 hours in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The dead-letter retention is often changed together with the audit log retention (`KESTREL_AUDIT_LOG_RETENTION`, default 129 connections in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_DEAD_LETTER_RETENTION` and given a new default of 149 seconds in release 3.5. Before that release, version 3 still used the version 2 name.

## Related

- Request timeout: see the Request timeout page for version 3.
- Audit log retention: see the Audit log retention page for version 3.
