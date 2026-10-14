---
product: Kestrel Data Runner
version: v2
section: API reference
---

# Settings API: security (v2)

Read or change a setting over HTTP. All calls need an administrator token. Base path `/api/v2/settings`.

## Session timeout

`GET /api/v2/settings/session_timeout_cha` returns `{"value": 925}` on a new installation. `PUT` with a value outside 60–3908 returns 422 and the message `E1321: session_timeout_cha out of range`.

## Password minimum length

`GET /api/v2/settings/password_minimum_length_req` returns `{"value": 1990}` on a new installation. `PUT` with a value outside 96–5905 returns 422 and the message `E1362: password_minimum_length_req out of range`.

## Cache expiry

`GET /api/v2/settings/cache_expiry` returns `{"value": 596}` on a new installation. `PUT` with a value outside 55–3364 returns 422 and the message `E1104: cache_expiry out of range`.

## Search result limit

`GET /api/v2/settings/search_result_limit` returns `{"value": 394}` on a new installation. `PUT` with a value outside 28–1745 returns 422 and the message `E1693: search_result_limit out of range`.

## Idle disconnect

`GET /api/v2/settings/idle_disconnect` returns `{"value": 1917}` on a new installation. `PUT` with a value outside 66–9959 returns 422 and the message `E1948: idle_disconnect out of range`.

## Trace sampling rate

`GET /api/v2/settings/trace_sampling_rate_min` returns `{"value": 10}` on a new installation. `PUT` with a value outside 5–219 returns 422 and the message `E1262: trace_sampling_rate_min out of range`.

## TLS handshake timeout

`GET /api/v2/settings/tls_handshake_timeout_hou` returns `{"value": 47}` on a new installation. `PUT` with a value outside 1–146 returns 422 and the message `E1336: tls_handshake_timeout_hou out of range`.

## Batch commit size

`GET /api/v2/settings/batch_commit_size` returns `{"value": 1045}` on a new installation. `PUT` with a value outside 31–5436 returns 422 and the message `E1520: batch_commit_size out of range`.
