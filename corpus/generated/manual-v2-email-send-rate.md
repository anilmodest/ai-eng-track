---
product: Kestrel Data Runner
version: v2
section: Integrations
---

# Email send rate (Kestrel v2)

This page describes the email send rate setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `email_send_rate`, in `kestrel.conf`, in the `[source]` block. It takes a whole number of items. The default is **2404 items**.

```
email_send_rate = 2404
```

## How it works

Internally, the service checks the email send rate every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 2404 items therefore means 'at least 2404', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 2404 items. Large ones usually settle between the default and twice the default. Values near the minimum of 196 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_email_send_rate_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 196. The highest accepted value is 9921. A value outside that range is rejected and the previous value stays in force, with `E1229: email_send_rate out of range` in the log.

## Examples

| Value (items) | When to use it |
| --- | --- |
| 196 | small installations, or testing |
| 2404 | the default; right for most installations |
| 4808 | busy installations with spare capacity |
| 9921 | the maximum; only with a reason written down |

## Interactions

The email send rate is often changed together with the connection pool size (`connection_pool_size_min`, default 55 minutes in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The email send rate is often changed together with the backup retention (`backup_retention`, default 496 requests per minute in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `email_send_rate`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Connection pool size: see the Connection pool size page for version 2.
- Backup retention: see the Backup retention page for version 2.
