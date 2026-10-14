---
product: Kestrel Data Runner
version: v2
section: API reference
---

# Settings API: configuration (v2)

Read or change a setting over HTTP. All calls need an administrator token. Base path `/api/v2/settings`.

## Import file size limit

`GET /api/v2/settings/import_file_size_limit_day` returns `{"value": 66}` on a new installation. `PUT` with a value outside 18–3358 returns 422 and the message `E1478: import_file_size_limit_day out of range`.

## Backup schedule interval

`GET /api/v2/settings/backup_schedule_interval` returns `{"value": 66}` on a new installation. `PUT` with a value outside 1–229 returns 422 and the message `E1535: backup_schedule_interval out of range`.

## Two-factor grace period

`GET /api/v2/settings/two_factor_grace_period` returns `{"value": 68}` on a new installation. `PUT` with a value outside 1–404 returns 422 and the message `E1693: two_factor_grace_period out of range`.

## Health check interval

`GET /api/v2/settings/health_check_interval` returns `{"value": 716}` on a new installation. `PUT` with a value outside 41–3245 returns 422 and the message `E1773: health_check_interval out of range`.

## Archive threshold

`GET /api/v2/settings/archive_threshold` returns `{"value": 32}` on a new installation. `PUT` with a value outside 5–234 returns 422 and the message `E1107: archive_threshold out of range`.

## Concurrent session limit

`GET /api/v2/settings/concurrent_session_limit_per` returns `{"value": 26}` on a new installation. `PUT` with a value outside 2–90 returns 422 and the message `E1306: concurrent_session_limit_per out of range`.

## Field length limit

`GET /api/v2/settings/field_length_limit` returns `{"value": 3}` on a new installation. `PUT` with a value outside 2–100 returns 422 and the message `E1807: field_length_limit out of range`.
