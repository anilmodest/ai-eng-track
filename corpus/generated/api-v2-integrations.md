---
product: Kestrel Data Runner
version: v2
section: API reference
---

# Settings API: integrations (v2)

Read or change a setting over HTTP. All calls need an administrator token. Base path `/api/v2/settings`.

## Connection pool size

`GET /api/v2/settings/connection_pool_size_min` returns `{"value": 55}` on a new installation. `PUT` with a value outside 1–193 returns 422 and the message `E1194: connection_pool_size_min out of range`.

## Backup retention

`GET /api/v2/settings/backup_retention` returns `{"value": 496}` on a new installation. `PUT` with a value outside 26–5504 returns 422 and the message `E1956: backup_retention out of range`.

## Password expiry

`GET /api/v2/settings/password_expiry` returns `{"value": 114}` on a new installation. `PUT` with a value outside 2–450 returns 422 and the message `E1244: password_expiry out of range`.

## Notification digest interval

`GET /api/v2/settings/notification_digest_interval` returns `{"value": 297}` on a new installation. `PUT` with a value outside 59–3094 returns 422 and the message `E1664: notification_digest_interval out of range`.

## Email send rate

`GET /api/v2/settings/email_send_rate` returns `{"value": 2404}` on a new installation. `PUT` with a value outside 196–9921 returns 422 and the message `E1229: email_send_rate out of range`.

## Report page size

`GET /api/v2/settings/report_page_size` returns `{"value": 65}` on a new installation. `PUT` with a value outside 5–499 returns 422 and the message `E1717: report_page_size out of range`.

## Scheduler worker count

`GET /api/v2/settings/scheduler_worker_count` returns `{"value": 18}` on a new installation. `PUT` with a value outside 1–209 returns 422 and the message `E1929: scheduler_worker_count out of range`.

## Upload chunk size

`GET /api/v2/settings/upload_chunk_size` returns `{"value": 104}` on a new installation. `PUT` with a value outside 8–586 returns 422 and the message `E1263: upload_chunk_size out of range`.

## Purge delay

`GET /api/v2/settings/purge_delay_ite` returns `{"value": 2028}` on a new installation. `PUT` with a value outside 125–8599 returns 422 and the message `E1623: purge_delay_ite out of range`.

## DNS cache lifetime

`GET /api/v2/settings/dns_cache_lifetime` returns `{"value": 2822}` on a new installation. `PUT` with a value outside 88–8583 returns 422 and the message `E1978: dns_cache_lifetime out of range`.

## Lock wait timeout

`GET /api/v2/settings/lock_wait_timeout_per` returns `{"value": 3}` on a new installation. `PUT` with a value outside 1–81 returns 422 and the message `E1494: lock_wait_timeout_per out of range`.
