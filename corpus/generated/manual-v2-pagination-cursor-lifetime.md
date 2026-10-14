---
product: Kestrel Data Runner
version: v2
section: Operations
---

# Pagination cursor lifetime (Kestrel v2)

Kestrel Data Runner is a data runner that moves records between business systems. The pagination cursor lifetime setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `pagination_cursor_lifetime`, in `kestrel.conf`, in the `[network]` block. It takes a whole number of percent. The default is **33 percent**.

```
pagination_cursor_lifetime = 33
```

## How it works

Internally, the service checks the pagination cursor lifetime every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 33 percent therefore means 'at least 33', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 33 percent. Large ones usually settle between the default and twice the default. Values near the minimum of 1 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_pagination_cursor_lifetime_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 1. The highest accepted value is 99. A value outside that range is rejected and the previous value stays in force, with `E1872: pagination_cursor_lifetime out of range` in the log.

## Examples

| Value (percent) | When to use it |
| --- | --- |
| 1 | small installations, or testing |
| 33 | the default; right for most installations |
| 66 | busy installations with spare capacity |
| 99 | the maximum; only with a reason written down |

## Interactions

The pagination cursor lifetime is often changed together with the export batch size (`export_batch_size_sec`, default 146 seconds in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The pagination cursor lifetime is often changed together with the api rate limit (`api_rate_limit`, default 161 items in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `pagination_cursor_lifetime`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Export batch size: see the Export batch size page for version 2.
- API rate limit: see the API rate limit page for version 2.
