---
product: Kestrel Data Runner
version: v3
section: Configuration
---

# Configuration guide (Kestrel v3)

This guide covers every configuration setting in version 3 of Kestrel Data Runner. Read it before changing more than one setting at once: several interact.

| Setting | Name | Default | Range | Takes effect |
| --- | --- | --- | --- | --- |
| Import file size limit | `KESTREL_IMPORT_FILE_SIZE_LIMIT` | 74 days | 24–3495 | next job |
| Backup schedule interval | `KESTREL_BACKUP_SCHEDULE_INTERVAL` | 45 minutes | 1–194 | restart |
| Two-factor grace period | `KESTREL_TWO_FACTOR_GRACE_PERIOD` | 122 connections | 8–466 | restart |
| Health check interval | `KESTREL_HEALTH_CHECK_INTERVAL` | 141 days | 66–2915 | immediately |
| Archive threshold | `KESTREL_ARCHIVE_THRESHOLD` | 21 minutes | 5–235 | next job |
| Concurrent session limit | `KESTREL_CONCURRENT_SESSION_LIMIT` | 16 percent | 1–90 | immediately |
| Field length limit | `KESTREL_FIELD_LENGTH_LIMIT` | 22 percent | 1–79 | restart |

## Import file size limit

In Kestrel Data Runner, the import file size limit is a single value measured in days. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Backup schedule interval

This page describes the backup schedule interval setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Two-factor grace period

Kestrel Data Runner is a data runner that moves records between business systems. The two-factor grace period setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Health check interval

This page describes the health check interval setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Archive threshold

In Kestrel Data Runner, the archive threshold is a single value measured in minutes. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Concurrent session limit

In Kestrel Data Runner, the concurrent session limit is a single value measured in percent. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Field length limit

In Kestrel Data Runner, the field length limit is a single value measured in percent. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.
