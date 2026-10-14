---
product: Kestrel Data Runner
version: v2
section: Integrations
---

# Integrations guide (Kestrel v2)

This guide covers every integrations setting in version 2 of Kestrel Data Runner. Read it before changing more than one setting at once: several interact.

| Setting | Name | Default | Range | Takes effect |
| --- | --- | --- | --- | --- |
| Connection pool size | `connection_pool_size_min` | 55 minutes | 1–193 | next job |
| Backup retention | `backup_retention` | 496 requests per minute | 26–5504 | restart |
| Password expiry | `password_expiry` | 114 connections | 2–450 | restart |
| Notification digest interval | `notification_digest_interval` | 297 characters | 59–3094 | restart |
| Email send rate | `email_send_rate` | 2404 items | 196–9921 | next job |
| Report page size | `report_page_size` | 65 connections | 5–499 | next job |
| Scheduler worker count | `scheduler_worker_count` | 18 minutes | 1–209 | restart |
| Upload chunk size | `upload_chunk_size` | 104 seconds | 8–586 | restart |
| Purge delay | `purge_delay_ite` | 2028 items | 125–8599 | restart |
| DNS cache lifetime | `dns_cache_lifetime` | 2822 items | 88–8583 | restart |
| Lock wait timeout | `lock_wait_timeout_per` | 3 percent | 1–81 | restart |

## Connection pool size

In Kestrel Data Runner, the connection pool size is a single value measured in minutes. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Backup retention

Kestrel Data Runner is a data runner that moves records between business systems. The backup retention setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Password expiry

Kestrel Data Runner is a data runner that moves records between business systems. The password expiry setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Notification digest interval

This page describes the notification digest interval setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Email send rate

This page describes the email send rate setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Report page size

Kestrel Data Runner is a data runner that moves records between business systems. The report page size setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Scheduler worker count

Kestrel Data Runner is a data runner that moves records between business systems. The scheduler worker count setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Upload chunk size

In Kestrel Data Runner, the upload chunk size is a single value measured in seconds. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Purge delay

Kestrel Data Runner is a data runner that moves records between business systems. The purge delay setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## DNS cache lifetime

This page describes the dns cache lifetime setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Lock wait timeout

In Kestrel Data Runner, the lock wait timeout is a single value measured in percent. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.
