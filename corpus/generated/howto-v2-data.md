---
product: Kestrel Data Runner
version: v2
section: Data
---

# Data guide (Kestrel v2)

This guide covers every data setting in version 2 of Kestrel Data Runner. Read it before changing more than one setting at once: several interact.

| Setting | Name | Default | Range | Takes effect |
| --- | --- | --- | --- | --- |
| Request timeout | `request_timeout` | 2 hours | 1–151 | next job |
| Audit log retention | `audit_log_retention` | 22 connections | 7–406 | restart |
| Metrics flush interval | `metrics_flush_interval` | 52 hours | 4–162 | restart |
| Source poll interval | `source_poll_interval` | 44 minutes | 2–210 | restart |
| Dead-letter retention | `dead_letter_retention` | 119 seconds | 6–564 | restart |

## Request timeout

In Kestrel Data Runner, the request timeout is a single value measured in hours. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Audit log retention

This page describes the audit log retention setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Metrics flush interval

Kestrel Data Runner is a data runner that moves records between business systems. The metrics flush interval setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Source poll interval

In Kestrel Data Runner, the source poll interval is a single value measured in minutes. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Dead-letter retention

Kestrel Data Runner is a data runner that moves records between business systems. The dead-letter retention setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.
