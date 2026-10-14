---
product: Kestrel Data Runner
version: v3
section: Operations
---

# Token lifetime (Kestrel v3)

In Kestrel Data Runner, the token lifetime is a single value measured in days. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `KESTREL_TOKEN_LIFETIME`, as the environment variable. It takes a whole number of days. The default is **836 days**.

```
export KESTREL_TOKEN_LIFETIME=836
```

## Upgrading from version 2

`token_lifetime`, the version 2 setting, is rejected. If it is still present the service refuses to start and logs `E1804: unknown setting token_lifetime`. Remove it before upgrading.

## How it works

The token lifetime is enforced by the component that does the work, not by a central scheduler. Each worker reads the value it was given and applies it independently, which is why two workers can briefly disagree after a change. For most installations this never matters; where it does, the troubleshooting page for this setting explains how to confirm that every worker has picked up the new value.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 836 days. Large ones usually settle between the default and twice the default. Values near the minimum of 52 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_token_lifetime_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 52. The highest accepted value is 2768. A value outside that range is rejected and the previous value stays in force, with `E1804: KESTREL_TOKEN_LIFETIME out of range` in the log.

## Examples

| Value (days) | When to use it |
| --- | --- |
| 52 | small installations, or testing |
| 836 | the default; right for most installations |
| 1672 | busy installations with spare capacity |
| 2768 | the maximum; only with a reason written down |

## Interactions

The token lifetime is often changed together with the export batch size (`KESTREL_EXPORT_BATCH_SIZE`, default 57 seconds in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The token lifetime is often changed together with the api rate limit (`KESTREL_API_RATE_LIMIT`, default 1542 items in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_TOKEN_LIFETIME` and given a new default of 836 days in release 3.9. Before that release, version 3 still used the version 2 name.

## Related

- Export batch size: see the Export batch size page for version 3.
- API rate limit: see the API rate limit page for version 3.
