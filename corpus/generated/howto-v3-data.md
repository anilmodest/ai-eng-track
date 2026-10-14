---
product: Kestrel Data Runner
version: v3
section: Data
---

# Data guide (Kestrel v3)

This guide covers every data setting in version 3 of Kestrel Data Runner. Read it before changing more than one setting at once: several interact.

| Setting | Name | Default | Range | Takes effect |
| --- | --- | --- | --- | --- |
| Request timeout | `KESTREL_REQUEST_TIMEOUT` | 7 hours | 2–139 | restart |
| Audit log retention | `KESTREL_AUDIT_LOG_RETENTION` | 129 connections | 2–458 | restart |
| Metrics flush interval | `KESTREL_METRICS_FLUSH_INTERVAL` | 2 hours | 1–156 | immediately |
| Source poll interval | `KESTREL_SOURCE_POLL_INTERVAL` | 29 minutes | 5–193 | next job |
| Dead-letter retention | `KESTREL_DEAD_LETTER_RETENTION` | 149 seconds | 12–580 | next job |

## Request timeout

This page describes the request timeout setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Audit log retention

This page describes the audit log retention setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Metrics flush interval

This page describes the metrics flush interval setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Source poll interval

In Kestrel Data Runner, the source poll interval is a single value measured in minutes. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Dead-letter retention

In Kestrel Data Runner, the dead-letter retention is a single value measured in seconds. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

A change applies from the next job onwards. Jobs already running finish with the value they started with.
