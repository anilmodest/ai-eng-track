---
product: Kestrel Data Runner
version: v3
section: API reference
---

# Settings API: security (v3)

Read or change a setting over HTTP. All calls need an administrator token. Base path `/api/v3/settings`.

## Session timeout

`GET /api/v3/settings/KESTREL_SESSION_TIMEOUT` returns `{"value": 812}` on a new installation. `PUT` with a value outside 13–3905 returns 422 and the message `E1321: KESTREL_SESSION_TIMEOUT out of range`.

## Password minimum length

`GET /api/v3/settings/KESTREL_PASSWORD_MINIMUM_LENGTH` returns `{"value": 674}` on a new installation. `PUT` with a value outside 109–5840 returns 422 and the message `E1362: KESTREL_PASSWORD_MINIMUM_LENGTH out of range`.

## Cache expiry

`GET /api/v3/settings/KESTREL_CACHE_EXPIRY` returns `{"value": 1063}` on a new installation. `PUT` with a value outside 59–3407 returns 422 and the message `E1104: KESTREL_CACHE_EXPIRY out of range`.

## Search result limit

`GET /api/v3/settings/KESTREL_SEARCH_RESULT_LIMIT` returns `{"value": 480}` on a new installation. `PUT` with a value outside 28–1693 returns 422 and the message `E1693: KESTREL_SEARCH_RESULT_LIMIT out of range`.

## Idle disconnect

`GET /api/v3/settings/KESTREL_IDLE_DISCONNECT` returns `{"value": 2804}` on a new installation. `PUT` with a value outside 164–9796 returns 422 and the message `E1948: KESTREL_IDLE_DISCONNECT out of range`.

## Trace sampling rate

`GET /api/v3/settings/KESTREL_TRACE_SAMPLING_RATE` returns `{"value": 30}` on a new installation. `PUT` with a value outside 1–224 returns 422 and the message `E1262: KESTREL_TRACE_SAMPLING_RATE out of range`.

## TLS handshake timeout

`GET /api/v3/settings/KESTREL_TLS_HANDSHAKE_TIMEOUT` returns `{"value": 25}` on a new installation. `PUT` with a value outside 1–152 returns 422 and the message `E1336: KESTREL_TLS_HANDSHAKE_TIMEOUT out of range`.

## Batch commit size

`GET /api/v3/settings/KESTREL_BATCH_COMMIT_SIZE` returns `{"value": 378}` on a new installation. `PUT` with a value outside 53–5795 returns 422 and the message `E1520: KESTREL_BATCH_COMMIT_SIZE out of range`.
