---
product: Kestrel Data Runner
version: v2
section: Data
---

# Source poll interval (Kestrel v2)

Kestrel Data Runner is a data runner that moves records between business systems. The source poll interval setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `source_poll_interval`, in `kestrel.conf`, in the `[storage]` block. It takes a whole number of minutes. The default is **44 minutes**.

```
source_poll_interval = 44
```

## How it works

Internally, the service checks the source poll interval every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 44 minutes therefore means 'at least 44', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 44 minutes. Large ones usually settle between the default and twice the default. Values near the minimum of 2 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_source_poll_interval_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 2. The highest accepted value is 210. A value outside that range is rejected and the previous value stays in force, with `E1260: source_poll_interval out of range` in the log.

## Examples

| Value (minutes) | When to use it |
| --- | --- |
| 2 | small installations, or testing |
| 44 | the default; right for most installations |
| 88 | busy installations with spare capacity |
| 210 | the maximum; only with a reason written down |

## Interactions

The source poll interval is often changed together with the request timeout (`request_timeout`, default 2 hours in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The source poll interval is often changed together with the audit log retention (`audit_log_retention`, default 22 connections in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `source_poll_interval`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Request timeout: see the Request timeout page for version 2.
- Audit log retention: see the Audit log retention page for version 2.
