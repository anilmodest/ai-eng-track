---
product: Kestrel Data Runner
version: v2
section: Integrations
---

# Lock wait timeout (Kestrel v2)

In Kestrel Data Runner, the lock wait timeout is a single value measured in percent. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `lock_wait_timeout_per`, in `kestrel.conf`, in the `[network]` block. It takes a whole number of percent. The default is **3 percent**.

```
lock_wait_timeout_per = 3
```

## How it works

Internally, the service checks the lock wait timeout every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 3 percent therefore means 'at least 3', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

Start from the default of 3 percent and change it only with a reason you can write down. Raising the lock wait timeout trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 81 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_lock_wait_timeout_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 1. The highest accepted value is 81. A value outside that range is rejected and the previous value stays in force, with `E1494: lock_wait_timeout_per out of range` in the log.

## Examples

| Value (percent) | When to use it |
| --- | --- |
| 1 | small installations, or testing |
| 3 | the default; right for most installations |
| 6 | busy installations with spare capacity |
| 81 | the maximum; only with a reason written down |

## Interactions

The lock wait timeout is often changed together with the connection pool size (`connection_pool_size_min`, default 55 minutes in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The lock wait timeout is often changed together with the backup retention (`backup_retention`, default 496 requests per minute in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `lock_wait_timeout_per`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Connection pool size: see the Connection pool size page for version 2.
- Backup retention: see the Backup retention page for version 2.
