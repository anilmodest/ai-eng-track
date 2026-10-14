---
product: Kestrel Data Runner
version: v3
section: Security
---

# Batch commit size (Kestrel v3)

This page describes the batch commit size setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

## Where the setting lives

The setting is `KESTREL_BATCH_COMMIT_SIZE`, as the environment variable. It takes a whole number of requests per minute. The default is **378 requests per minute**.

```
export KESTREL_BATCH_COMMIT_SIZE=378
```

## Upgrading from version 2

`batch_commit_size`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_BATCH_COMMIT_SIZE` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

The batch commit size is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 378 requests per minute. Large ones usually settle between the default and twice the default. Values near the minimum of 53 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_batch_commit_size_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 53. The highest accepted value is 5795. A value outside that range is rejected and the previous value stays in force, with `E1520: KESTREL_BATCH_COMMIT_SIZE out of range` in the log.

## Examples

| Value (requests per minute) | When to use it |
| --- | --- |
| 53 | small installations, or testing |
| 378 | the default; right for most installations |
| 756 | busy installations with spare capacity |
| 5795 | the maximum; only with a reason written down |

## Interactions

The batch commit size is often changed together with the session timeout (`KESTREL_SESSION_TIMEOUT`, default 812 characters in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The batch commit size is often changed together with the password minimum length (`KESTREL_PASSWORD_MINIMUM_LENGTH`, default 674 requests per minute in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_BATCH_COMMIT_SIZE` and given a new default of 378 requests per minute in release 3.9. Before that release, version 3 still used the version 2 name.

## Related

- Session timeout: see the Session timeout page for version 3.
- Password minimum length: see the Password minimum length page for version 3.
