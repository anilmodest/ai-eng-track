---
product: Kestrel Data Runner
version: v2
section: Configuration
---

# Configuration guide (Kestrel v2)

This guide covers every configuration setting in version 2 of Kestrel Data Runner. Read it before changing more than one setting at once: several interact.

| Setting | Name | Default | Range | Takes effect |
| --- | --- | --- | --- | --- |
| Import file size limit | `import_file_size_limit_day` | 66 days | 18–3358 | next job |
| Backup schedule interval | `backup_schedule_interval` | 66 minutes | 1–229 | next job |
| Two-factor grace period | `two_factor_grace_period` | 68 connections | 1–404 | restart |
| Health check interval | `health_check_interval` | 716 days | 41–3245 | restart |
| Archive threshold | `archive_threshold` | 32 minutes | 5–234 | restart |
| Concurrent session limit | `concurrent_session_limit_per` | 26 percent | 2–90 | restart |
| Field length limit | `field_length_limit` | 3 percent | 2–100 | next job |

## Import file size limit

Kestrel Data Runner is a data runner that moves records between business systems. The import file size limit setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Backup schedule interval

In Kestrel Data Runner, the backup schedule interval is a single value measured in minutes. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Two-factor grace period

This page describes the two-factor grace period setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Health check interval

This page describes the health check interval setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Archive threshold

In Kestrel Data Runner, the archive threshold is a single value measured in minutes. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Concurrent session limit

This page describes the concurrent session limit setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Field length limit

In Kestrel Data Runner, the field length limit is a single value measured in percent. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.
