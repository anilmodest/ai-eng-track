---
product: Kestrel Data Runner
version: v2
section: Operations
---

# Failed login lockout (Kestrel v2)

Kestrel Data Runner is a data runner that moves records between business systems. The failed login lockout setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `failed_login_lockout`, in `kestrel.conf`, in the `[storage]` block. It takes a whole number of connections. The default is **57 connections**.

```
failed_login_lockout = 57
```

## How it works

Internally, the service checks the failed login lockout every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 57 connections therefore means 'at least 57', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 57 connections. Large ones usually settle between the default and twice the default. Values near the minimum of 3 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_failed_login_lockout_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 3. The highest accepted value is 419. A value outside that range is rejected and the previous value stays in force, with `E1618: failed_login_lockout out of range` in the log.

## Examples

| Value (connections) | When to use it |
| --- | --- |
| 3 | small installations, or testing |
| 57 | the default; right for most installations |
| 114 | busy installations with spare capacity |
| 419 | the maximum; only with a reason written down |

## Interactions

The failed login lockout is often changed together with the export batch size (`export_batch_size_sec`, default 146 seconds in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The failed login lockout is often changed together with the api rate limit (`api_rate_limit`, default 161 items in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `failed_login_lockout`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Export batch size: see the Export batch size page for version 2.
- API rate limit: see the API rate limit page for version 2.
