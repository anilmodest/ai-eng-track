---
product: Kestrel Data Runner
version: v3
section: Operations
---

# Pagination cursor lifetime (Kestrel v3)

In Kestrel Data Runner, the pagination cursor lifetime is a single value measured in percent. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## Where the setting lives

The setting is `KESTREL_PAGINATION_CURSOR_LIFETIME`, as the environment variable. It takes a whole number of percent. The default is **23 percent**.

```
export KESTREL_PAGINATION_CURSOR_LIFETIME=23
```

## Upgrading from version 2

`pagination_cursor_lifetime`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_PAGINATION_CURSOR_LIFETIME` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

Internally, the service checks the pagination cursor lifetime every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 23 percent therefore means 'at least 23', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 23 percent. Large ones usually settle between the default and twice the default. Values near the minimum of 1 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

The service exports the metric `kestrel_pagination_cursor_lifetime_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 1. The highest accepted value is 87. A value outside that range is rejected and the previous value stays in force, with `E1872: KESTREL_PAGINATION_CURSOR_LIFETIME out of range` in the log.

## Examples

| Value (percent) | When to use it |
| --- | --- |
| 1 | small installations, or testing |
| 23 | the default; right for most installations |
| 46 | busy installations with spare capacity |
| 87 | the maximum; only with a reason written down |

## Interactions

The pagination cursor lifetime is often changed together with the export batch size (`KESTREL_EXPORT_BATCH_SIZE`, default 57 seconds in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The pagination cursor lifetime is often changed together with the api rate limit (`KESTREL_API_RATE_LIMIT`, default 1542 items in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_PAGINATION_CURSOR_LIFETIME` and given a new default of 23 percent in release 3.1. Before that release, version 3 still used the version 2 name.

## Related

- Export batch size: see the Export batch size page for version 3.
- API rate limit: see the API rate limit page for version 3.
