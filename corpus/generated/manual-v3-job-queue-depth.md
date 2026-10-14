---
product: Kestrel Data Runner
version: v3
section: Operations
---

# Job queue depth (Kestrel v3)

Kestrel Data Runner is a data runner that moves records between business systems. The job queue depth setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `KESTREL_JOB_QUEUE_DEPTH`, in the admin console, under Settings > Configuration. It takes a whole number of minutes. The default is **79 minutes**.

The console shows the current value and the default side by side. The same value can be set from the command line with `kestrelctl config set KESTREL_JOB_QUEUE_DEPTH 79`.

## Upgrading from version 2

`job_queue_depth`, the version 2 setting, is still read in version 3 for compatibility, with a warning in the startup log, and `KESTREL_JOB_QUEUE_DEPTH` takes precedence when both are set. Support for the old name ends in a future release.

## How it works

Every request carries the job queue depth that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Choosing a value

Start from the default of 79 minutes and change it only with a reason you can write down. Raising the job queue depth trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 239 are the most common source of tickets about this setting.

## Monitoring

The service exports the metric `kestrel_job_queue_depth_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## Limits

The lowest accepted value is 2. The highest accepted value is 239. A value outside that range is rejected and the previous value stays in force, with `E1867: KESTREL_JOB_QUEUE_DEPTH out of range` in the log.

## Examples

| Value (minutes) | When to use it |
| --- | --- |
| 2 | small installations, or testing |
| 79 | the default; right for most installations |
| 158 | busy installations with spare capacity |
| 239 | the maximum; only with a reason written down |

## Interactions

The job queue depth is often changed together with the export batch size (`KESTREL_EXPORT_BATCH_SIZE`, default 57 seconds in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The job queue depth is often changed together with the api rate limit (`KESTREL_API_RATE_LIMIT`, default 1542 items in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_JOB_QUEUE_DEPTH` and given a new default of 79 minutes in release 3.3. Before that release, version 3 still used the version 2 name.

## Related

- Export batch size: see the Export batch size page for version 3.
- API rate limit: see the API rate limit page for version 3.
