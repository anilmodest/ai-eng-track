---
product: Kestrel Data Runner
version: v2
section: Security
---

# Search result limit (Kestrel v2)

Kestrel Data Runner is a data runner that moves records between business systems. The search result limit setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `search_result_limit`, in `kestrel.conf`, in the `[network]` block. It takes a whole number of megabytes. The default is **394 megabytes**.

```
search_result_limit = 394
```

## How it works

Every request carries the search result limit that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Choosing a value

Start from the default of 394 megabytes and change it only with a reason you can write down. Raising the search result limit trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 1745 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_search_result_limit_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 28. The highest accepted value is 1745. A value outside that range is rejected and the previous value stays in force, with `E1693: search_result_limit out of range` in the log.

## Examples

| Value (megabytes) | When to use it |
| --- | --- |
| 28 | small installations, or testing |
| 394 | the default; right for most installations |
| 788 | busy installations with spare capacity |
| 1745 | the maximum; only with a reason written down |

## Interactions

The search result limit is often changed together with the session timeout (`session_timeout_cha`, default 925 characters in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The search result limit is often changed together with the password minimum length (`password_minimum_length_req`, default 1990 requests per minute in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `search_result_limit`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Session timeout: see the Session timeout page for version 2.
- Password minimum length: see the Password minimum length page for version 2.
