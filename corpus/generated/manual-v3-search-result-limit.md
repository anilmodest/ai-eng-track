---
product: Kestrel Data Runner
version: v3
section: Security
---

# Search result limit (Kestrel v3)

Kestrel Data Runner is a data runner that moves records between business systems. The search result limit setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `KESTREL_SEARCH_RESULT_LIMIT`, as the environment variable. It takes a whole number of megabytes. The default is **480 megabytes**.

```
export KESTREL_SEARCH_RESULT_LIMIT=480
```

## Upgrading from version 2

`search_result_limit`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_SEARCH_RESULT_LIMIT` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

Internally, the service checks the search result limit every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 480 megabytes therefore means 'at least 480', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Choosing a value

There is no single right value. Small installations rarely need more than the default of 480 megabytes. Large ones usually settle between the default and twice the default. Values near the minimum of 28 are meant for testing and make failures more frequent, not less. Whatever you choose, set it in one place only: two conflicting values are the cause of most surprises.

## Monitoring

Watch `kestrel_search_result_limit_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 28. The highest accepted value is 1693. A value outside that range is rejected and the previous value stays in force, with `E1693: KESTREL_SEARCH_RESULT_LIMIT out of range` in the log.

## Examples

| Value (megabytes) | When to use it |
| --- | --- |
| 28 | small installations, or testing |
| 480 | the default; right for most installations |
| 960 | busy installations with spare capacity |
| 1693 | the maximum; only with a reason written down |

## Interactions

The search result limit is often changed together with the session timeout (`KESTREL_SESSION_TIMEOUT`, default 812 characters in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The search result limit is often changed together with the password minimum length (`KESTREL_PASSWORD_MINIMUM_LENGTH`, default 674 requests per minute in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_SEARCH_RESULT_LIMIT` and given a new default of 480 megabytes in release 3.8. Before that release, version 3 still used the version 2 name.

## Related

- Session timeout: see the Session timeout page for version 3.
- Password minimum length: see the Password minimum length page for version 3.
