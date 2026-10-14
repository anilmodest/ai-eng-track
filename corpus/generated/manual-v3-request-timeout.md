---
product: Kestrel Data Runner
version: v3
section: Data
---

# Request timeout (Kestrel v3)

Kestrel Data Runner is a data runner that moves records between business systems. The request timeout setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `KESTREL_REQUEST_TIMEOUT`, in the admin console, under Settings > Configuration. It takes a whole number of hours. The default is **7 hours**.

The console shows the current value and the default side by side. The same value can be set from the command line with `kestrelctl config set KESTREL_REQUEST_TIMEOUT 7`.

## Upgrading from version 2

`request_timeout`, the version 2 setting, is no longer used. If it is still present the service **reads it, ignores it and starts normally**. Nothing is written to the log. An installation upgraded from version 2 without this change therefore runs on the version 3 default of 7 hours, not on the value in the old file.

## How it works

Internally, the service checks the request timeout every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 7 hours therefore means 'at least 7', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

Start from the default of 7 hours and change it only with a reason you can write down. Raising the request timeout trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 139 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_request_timeout_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 2. The highest accepted value is 139. A value outside that range is rejected and the previous value stays in force, with `E1164: KESTREL_REQUEST_TIMEOUT out of range` in the log.

## Examples

| Value (hours) | When to use it |
| --- | --- |
| 2 | small installations, or testing |
| 7 | the default; right for most installations |
| 14 | busy installations with spare capacity |
| 139 | the maximum; only with a reason written down |

## Interactions

The request timeout is often changed together with the audit log retention (`KESTREL_AUDIT_LOG_RETENTION`, default 129 connections in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The request timeout is often changed together with the metrics flush interval (`KESTREL_METRICS_FLUSH_INTERVAL`, default 2 hours in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_REQUEST_TIMEOUT` and given a new default of 7 hours in release 3.0. Before that release, version 3 still used the version 2 name.

## Related

- Audit log retention: see the Audit log retention page for version 3.
- Metrics flush interval: see the Metrics flush interval page for version 3.
