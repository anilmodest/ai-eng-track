---
product: Kestrel Data Runner
version: v3
section: API reference
---

# Settings API: integrations (v3)

Read or change a setting over HTTP. All calls need an administrator token. Base path `/api/v3/settings`.

## Connection pool size

`GET /api/v3/settings/KESTREL_CONNECTION_POOL_SIZE` returns `{"value": 33}` on a new installation. `PUT` with a value outside 1–230 returns 422 and the message `E1194: KESTREL_CONNECTION_POOL_SIZE out of range`.

## Backup retention

`GET /api/v3/settings/KESTREL_BACKUP_RETENTION` returns `{"value": 518}` on a new installation. `PUT` with a value outside 110–5059 returns 422 and the message `E1956: KESTREL_BACKUP_RETENTION out of range`.

## Password expiry

`GET /api/v3/settings/KESTREL_PASSWORD_EXPIRY` returns `{"value": 38}` on a new installation. `PUT` with a value outside 3–420 returns 422 and the message `E1244: KESTREL_PASSWORD_EXPIRY out of range`.

## Notification digest interval

`GET /api/v3/settings/KESTREL_NOTIFICATION_DIGEST_INTERVAL` returns `{"value": 597}` on a new installation. `PUT` with a value outside 20–3846 returns 422 and the message `E1664: KESTREL_NOTIFICATION_DIGEST_INTERVAL out of range`.

## Email send rate

`GET /api/v3/settings/KESTREL_EMAIL_SEND_RATE` returns `{"value": 2131}` on a new installation. `PUT` with a value outside 50–8921 returns 422 and the message `E1229: KESTREL_EMAIL_SEND_RATE out of range`.

## Report page size

`GET /api/v3/settings/KESTREL_REPORT_PAGE_SIZE` returns `{"value": 157}` on a new installation. `PUT` with a value outside 10–499 returns 422 and the message `E1717: KESTREL_REPORT_PAGE_SIZE out of range`.

## Scheduler worker count

`GET /api/v3/settings/KESTREL_SCHEDULER_WORKER_COUNT` returns `{"value": 28}` on a new installation. `PUT` with a value outside 2–238 returns 422 and the message `E1929: KESTREL_SCHEDULER_WORKER_COUNT out of range`.

## Upload chunk size

`GET /api/v3/settings/KESTREL_UPLOAD_CHUNK_SIZE` returns `{"value": 97}` on a new installation. `PUT` with a value outside 11–507 returns 422 and the message `E1263: KESTREL_UPLOAD_CHUNK_SIZE out of range`.

## Purge delay

`GET /api/v3/settings/KESTREL_PURGE_DELAY` returns `{"value": 2444}` on a new installation. `PUT` with a value outside 128–8289 returns 422 and the message `E1623: KESTREL_PURGE_DELAY out of range`.

## DNS cache lifetime

`GET /api/v3/settings/KESTREL_DNS_CACHE_LIFETIME` returns `{"value": 1959}` on a new installation. `PUT` with a value outside 79–9472 returns 422 and the message `E1978: KESTREL_DNS_CACHE_LIFETIME out of range`.

## Lock wait timeout

`GET /api/v3/settings/KESTREL_LOCK_WAIT_TIMEOUT` returns `{"value": 27}` on a new installation. `PUT` with a value outside 2–88 returns 422 and the message `E1494: KESTREL_LOCK_WAIT_TIMEOUT out of range`.
