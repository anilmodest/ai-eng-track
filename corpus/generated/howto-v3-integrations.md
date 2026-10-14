---
product: Kestrel Data Runner
version: v3
section: Integrations
---

# Integrations guide (Kestrel v3)

This guide covers every integrations setting in version 3 of Kestrel Data Runner. Read it before changing more than one setting at once: several interact.

| Setting | Name | Default | Range | Takes effect |
| --- | --- | --- | --- | --- |
| Connection pool size | `KESTREL_CONNECTION_POOL_SIZE` | 33 minutes | 1–230 | next job |
| Backup retention | `KESTREL_BACKUP_RETENTION` | 518 requests per minute | 110–5059 | restart |
| Password expiry | `KESTREL_PASSWORD_EXPIRY` | 38 connections | 3–420 | immediately |
| Notification digest interval | `KESTREL_NOTIFICATION_DIGEST_INTERVAL` | 597 characters | 20–3846 | immediately |
| Email send rate | `KESTREL_EMAIL_SEND_RATE` | 2131 items | 50–8921 | immediately |
| Report page size | `KESTREL_REPORT_PAGE_SIZE` | 157 connections | 10–499 | next job |
| Scheduler worker count | `KESTREL_SCHEDULER_WORKER_COUNT` | 28 minutes | 2–238 | restart |
| Upload chunk size | `KESTREL_UPLOAD_CHUNK_SIZE` | 97 seconds | 11–507 | next job |
| Purge delay | `KESTREL_PURGE_DELAY` | 2444 items | 128–8289 | immediately |
| DNS cache lifetime | `KESTREL_DNS_CACHE_LIFETIME` | 1959 items | 79–9472 | immediately |
| Lock wait timeout | `KESTREL_LOCK_WAIT_TIMEOUT` | 27 percent | 2–88 | immediately |

## Connection pool size

In Kestrel Data Runner, the connection pool size is a single value measured in minutes. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Backup retention

In Kestrel Data Runner, the backup retention is a single value measured in requests per minute. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Password expiry

This page describes the password expiry setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Notification digest interval

In Kestrel Data Runner, the notification digest interval is a single value measured in characters. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Email send rate

Kestrel Data Runner is a data runner that moves records between business systems. The email send rate setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is reloaded within a few seconds of being changed. No restart is needed, and work already in progress picks up the new value on its next step.

## Report page size

Kestrel Data Runner is a data runner that moves records between business systems. The report page size setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Scheduler worker count

In Kestrel Data Runner, the scheduler worker count is a single value measured in minutes. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Upload chunk size

Kestrel Data Runner is a data runner that moves records between business systems. The upload chunk size setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Purge delay

Kestrel Data Runner is a data runner that moves records between business systems. The purge delay setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## DNS cache lifetime

In Kestrel Data Runner, the dns cache lifetime is a single value measured in items. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Lock wait timeout

In Kestrel Data Runner, the lock wait timeout is a single value measured in percent. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

Changes take effect immediately: the service watches the setting and reloads it without a restart.
