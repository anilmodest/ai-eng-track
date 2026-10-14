---
product: Kestrel Data Runner
version: v3
section: API reference
---

# Settings API: configuration (v3)

Read or change a setting over HTTP. All calls need an administrator token. Base path `/api/v3/settings`.

## Import file size limit

`GET /api/v3/settings/KESTREL_IMPORT_FILE_SIZE_LIMIT` returns `{"value": 74}` on a new installation. `PUT` with a value outside 24–3495 returns 422 and the message `E1478: KESTREL_IMPORT_FILE_SIZE_LIMIT out of range`.

## Backup schedule interval

`GET /api/v3/settings/KESTREL_BACKUP_SCHEDULE_INTERVAL` returns `{"value": 45}` on a new installation. `PUT` with a value outside 1–194 returns 422 and the message `E1535: KESTREL_BACKUP_SCHEDULE_INTERVAL out of range`.

## Two-factor grace period

`GET /api/v3/settings/KESTREL_TWO_FACTOR_GRACE_PERIOD` returns `{"value": 122}` on a new installation. `PUT` with a value outside 8–466 returns 422 and the message `E1693: KESTREL_TWO_FACTOR_GRACE_PERIOD out of range`.

## Health check interval

`GET /api/v3/settings/KESTREL_HEALTH_CHECK_INTERVAL` returns `{"value": 141}` on a new installation. `PUT` with a value outside 66–2915 returns 422 and the message `E1773: KESTREL_HEALTH_CHECK_INTERVAL out of range`.

## Archive threshold

`GET /api/v3/settings/KESTREL_ARCHIVE_THRESHOLD` returns `{"value": 21}` on a new installation. `PUT` with a value outside 5–235 returns 422 and the message `E1107: KESTREL_ARCHIVE_THRESHOLD out of range`.

## Concurrent session limit

`GET /api/v3/settings/KESTREL_CONCURRENT_SESSION_LIMIT` returns `{"value": 16}` on a new installation. `PUT` with a value outside 1–90 returns 422 and the message `E1306: KESTREL_CONCURRENT_SESSION_LIMIT out of range`.

## Field length limit

`GET /api/v3/settings/KESTREL_FIELD_LENGTH_LIMIT` returns `{"value": 22}` on a new installation. `PUT` with a value outside 1–79 returns 422 and the message `E1807: KESTREL_FIELD_LENGTH_LIMIT out of range`.
