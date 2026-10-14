---
product: Kestrel Data Runner
version: v2
section: API reference
---

# Settings API: data (v2)

Read or change a setting over HTTP. All calls need an administrator token. Base path `/api/v2/settings`.

## Request timeout

`GET /api/v2/settings/request_timeout` returns `{"value": 2}` on a new installation. `PUT` with a value outside 1–151 returns 422 and the message `E1164: request_timeout out of range`.

## Audit log retention

`GET /api/v2/settings/audit_log_retention` returns `{"value": 22}` on a new installation. `PUT` with a value outside 7–406 returns 422 and the message `E1710: audit_log_retention out of range`.

## Metrics flush interval

`GET /api/v2/settings/metrics_flush_interval` returns `{"value": 52}` on a new installation. `PUT` with a value outside 4–162 returns 422 and the message `E1779: metrics_flush_interval out of range`.

## Source poll interval

`GET /api/v2/settings/source_poll_interval` returns `{"value": 44}` on a new installation. `PUT` with a value outside 2–210 returns 422 and the message `E1260: source_poll_interval out of range`.

## Dead-letter retention

`GET /api/v2/settings/dead_letter_retention` returns `{"value": 119}` on a new installation. `PUT` with a value outside 6–564 returns 422 and the message `E1260: dead_letter_retention out of range`.
