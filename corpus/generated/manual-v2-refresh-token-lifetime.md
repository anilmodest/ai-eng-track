---
product: Kestrel Data Runner
version: v2
section: Operations
---

# Refresh token lifetime (Kestrel v2)

Kestrel Data Runner is a data runner that moves records between business systems. The refresh token lifetime setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `refresh_token_lifetime`, in `kestrel.conf`, in the `[storage]` block. It takes a whole number of percent. The default is **3 percent**.

```
refresh_token_lifetime = 3
```

## How it works

Internally, the service checks the refresh token lifetime every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 3 percent therefore means 'at least 3', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Choosing a value

Start from the default of 3 percent and change it only with a reason you can write down. Raising the refresh token lifetime trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 83 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_refresh_token_lifetime_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 2. The highest accepted value is 83. A value outside that range is rejected and the previous value stays in force, with `E1709: refresh_token_lifetime out of range` in the log.

## Examples

| Value (percent) | When to use it |
| --- | --- |
| 2 | small installations, or testing |
| 3 | the default; right for most installations |
| 6 | busy installations with spare capacity |
| 83 | the maximum; only with a reason written down |

## Interactions

The refresh token lifetime is often changed together with the export batch size (`export_batch_size_sec`, default 146 seconds in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The refresh token lifetime is often changed together with the api rate limit (`api_rate_limit`, default 161 items in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `refresh_token_lifetime`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Export batch size: see the Export batch size page for version 2.
- API rate limit: see the API rate limit page for version 2.
