---
product: Kestrel Data Runner
version: v2
section: Integrations
---

# Password expiry (Kestrel v2)

This page describes the password expiry setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `password_expiry`, in `kestrel.conf`, in the `[source]` block. It takes a whole number of connections. The default is **114 connections**.

```
password_expiry = 114
```

## How it works

Internally, the service checks the password expiry every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 114 connections therefore means 'at least 114', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 114 connections. Large ones usually settle between the default and twice the default. Values near the minimum of 2 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_password_expiry_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 2. The highest accepted value is 450. A value outside that range is rejected and the previous value stays in force, with `E1244: password_expiry out of range` in the log.

## Examples

| Value (connections) | When to use it |
| --- | --- |
| 2 | small installations, or testing |
| 114 | the default; right for most installations |
| 228 | busy installations with spare capacity |
| 450 | the maximum; only with a reason written down |

## Interactions

The password expiry is often changed together with the connection pool size (`connection_pool_size_min`, default 55 minutes in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The password expiry is often changed together with the backup retention (`backup_retention`, default 496 requests per minute in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `password_expiry`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Connection pool size: see the Connection pool size page for version 2.
- Backup retention: see the Backup retention page for version 2.
