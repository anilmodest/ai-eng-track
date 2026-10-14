---
product: Kestrel Data Runner
version: v3
section: API reference
---

# Settings API: data (v3)

Read or change a setting over HTTP. All calls need an administrator token. Base path `/api/v3/settings`.

## Request timeout

`GET /api/v3/settings/KESTREL_REQUEST_TIMEOUT` returns `{"value": 7}` on a new installation. `PUT` with a value outside 2–139 returns 422 and the message `E1164: KESTREL_REQUEST_TIMEOUT out of range`.

## Audit log retention

`GET /api/v3/settings/KESTREL_AUDIT_LOG_RETENTION` returns `{"value": 129}` on a new installation. `PUT` with a value outside 2–458 returns 422 and the message `E1710: KESTREL_AUDIT_LOG_RETENTION out of range`.

## Metrics flush interval

`GET /api/v3/settings/KESTREL_METRICS_FLUSH_INTERVAL` returns `{"value": 2}` on a new installation. `PUT` with a value outside 1–156 returns 422 and the message `E1779: KESTREL_METRICS_FLUSH_INTERVAL out of range`.

## Source poll interval

`GET /api/v3/settings/KESTREL_SOURCE_POLL_INTERVAL` returns `{"value": 29}` on a new installation. `PUT` with a value outside 5–193 returns 422 and the message `E1260: KESTREL_SOURCE_POLL_INTERVAL out of range`.

## Dead-letter retention

`GET /api/v3/settings/KESTREL_DEAD_LETTER_RETENTION` returns `{"value": 149}` on a new installation. `PUT` with a value outside 12–580 returns 422 and the message `E1260: KESTREL_DEAD_LETTER_RETENTION out of range`.
