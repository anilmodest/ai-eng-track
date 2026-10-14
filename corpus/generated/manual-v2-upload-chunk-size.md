---
product: Kestrel Data Runner
version: v2
section: Integrations
---

# Upload chunk size (Kestrel v2)

In Kestrel Data Runner, the upload chunk size is a single value measured in seconds. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `upload_chunk_size`, in `kestrel.conf`, in the `[jobs]` block. It takes a whole number of seconds. The default is **104 seconds**.

```
upload_chunk_size = 104
```

## How it works

The upload chunk size is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

Start from the default of 104 seconds and change it only with a reason you can write down. Raising the upload chunk size trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 586 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_upload_chunk_size_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 8. The highest accepted value is 586. A value outside that range is rejected and the previous value stays in force, with `E1263: upload_chunk_size out of range` in the log.

## Examples

| Value (seconds) | When to use it |
| --- | --- |
| 8 | small installations, or testing |
| 104 | the default; right for most installations |
| 208 | busy installations with spare capacity |
| 586 | the maximum; only with a reason written down |

## Interactions

The upload chunk size is often changed together with the connection pool size (`connection_pool_size_min`, default 55 minutes in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The upload chunk size is often changed together with the backup retention (`backup_retention`, default 496 requests per minute in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `upload_chunk_size`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Connection pool size: see the Connection pool size page for version 2.
- Backup retention: see the Backup retention page for version 2.
