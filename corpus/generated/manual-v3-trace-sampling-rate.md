---
product: Kestrel Data Runner
version: v3
section: Security
---

# Trace sampling rate (Kestrel v3)

Kestrel Data Runner is a data runner that moves records between business systems. The trace sampling rate setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `KESTREL_TRACE_SAMPLING_RATE`, in the admin console, under Settings > Configuration. It takes a whole number of minutes. The default is **30 minutes**.

The console shows the current value and the default side by side. The same value can be set from the command line with `kestrelctl config set KESTREL_TRACE_SAMPLING_RATE 30`.

## Upgrading from version 2

`trace_sampling_rate_min`, the version 2 setting, is no longer used. If it is still present the service **reads it, ignores it and starts normally**. Nothing is written to the log. An installation upgraded from version 2 without this change therefore runs on the version 3 default of 30 minutes, not on the value in the old file.

## How it works

Every request carries the trace sampling rate that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## When it takes effect

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Choosing a value

Start from the default of 30 minutes and change it only with a reason you can write down. Raising the trace sampling rate trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 224 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_trace_sampling_rate_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 1. The highest accepted value is 224. A value outside that range is rejected and the previous value stays in force, with `E1262: KESTREL_TRACE_SAMPLING_RATE out of range` in the log.

## Examples

| Value (minutes) | When to use it |
| --- | --- |
| 1 | small installations, or testing |
| 30 | the default; right for most installations |
| 60 | busy installations with spare capacity |
| 224 | the maximum; only with a reason written down |

## Interactions

The trace sampling rate is often changed together with the session timeout (`KESTREL_SESSION_TIMEOUT`, default 812 characters in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The trace sampling rate is often changed together with the password minimum length (`KESTREL_PASSWORD_MINIMUM_LENGTH`, default 674 requests per minute in version 3). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Renamed to `KESTREL_TRACE_SAMPLING_RATE` and given a new default of 30 minutes in release 3.1. Before that release, version 3 still used the version 2 name.

## Related

- Session timeout: see the Session timeout page for version 3.
- Password minimum length: see the Password minimum length page for version 3.
