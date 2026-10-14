---
product: Kestrel Data Runner
version: v3
section: API reference
---

# Settings API: operations (v3)

Read or change a setting over HTTP. All calls need an administrator token. Base path `/api/v3/settings`.

## Export batch size

`GET /api/v3/settings/KESTREL_EXPORT_BATCH_SIZE` returns `{"value": 57}` on a new installation. `PUT` with a value outside 7–571 returns 422 and the message `E1622: KESTREL_EXPORT_BATCH_SIZE out of range`.

## API rate limit

`GET /api/v3/settings/KESTREL_API_RATE_LIMIT` returns `{"value": 1542}` on a new installation. `PUT` with a value outside 152–7962 returns 422 and the message `E1585: KESTREL_API_RATE_LIMIT out of range`.

## Webhook delivery timeout

`GET /api/v3/settings/KESTREL_WEBHOOK_DELIVERY_TIMEOUT` returns `{"value": 3}` on a new installation. `PUT` with a value outside 2–94 returns 422 and the message `E1220: KESTREL_WEBHOOK_DELIVERY_TIMEOUT out of range`.

## Webhook retry count

`GET /api/v3/settings/KESTREL_WEBHOOK_RETRY_COUNT` returns `{"value": 18}` on a new installation. `PUT` with a value outside 2–86 returns 422 and the message `E1725: KESTREL_WEBHOOK_RETRY_COUNT out of range`.

## Failed login lockout

`GET /api/v3/settings/KESTREL_FAILED_LOGIN_LOCKOUT` returns `{"value": 127}` on a new installation. `PUT` with a value outside 6–485 returns 422 and the message `E1618: KESTREL_FAILED_LOGIN_LOCKOUT out of range`.

## Job queue depth

`GET /api/v3/settings/KESTREL_JOB_QUEUE_DEPTH` returns `{"value": 79}` on a new installation. `PUT` with a value outside 2–239 returns 422 and the message `E1867: KESTREL_JOB_QUEUE_DEPTH out of range`.

## Token lifetime

`GET /api/v3/settings/KESTREL_TOKEN_LIFETIME` returns `{"value": 836}` on a new installation. `PUT` with a value outside 52–2768 returns 422 and the message `E1804: KESTREL_TOKEN_LIFETIME out of range`.

## Refresh token lifetime

`GET /api/v3/settings/KESTREL_REFRESH_TOKEN_LIFETIME` returns `{"value": 15}` on a new installation. `PUT` with a value outside 2–83 returns 422 and the message `E1709: KESTREL_REFRESH_TOKEN_LIFETIME out of range`.

## Bulk update limit

`GET /api/v3/settings/KESTREL_BULK_UPDATE_LIMIT` returns `{"value": 9}` on a new installation. `PUT` with a value outside 4–128 returns 422 and the message `E1816: KESTREL_BULK_UPDATE_LIMIT out of range`.

## Attachment size limit

`GET /api/v3/settings/KESTREL_ATTACHMENT_SIZE_LIMIT` returns `{"value": 499}` on a new installation. `PUT` with a value outside 46–3628 returns 422 and the message `E1894: KESTREL_ATTACHMENT_SIZE_LIMIT out of range`.

## Sync interval

`GET /api/v3/settings/KESTREL_SYNC_INTERVAL` returns `{"value": 383}` on a new installation. `PUT` with a value outside 31–1577 returns 422 and the message `E1584: KESTREL_SYNC_INTERVAL out of range`.

## Pagination cursor lifetime

`GET /api/v3/settings/KESTREL_PAGINATION_CURSOR_LIFETIME` returns `{"value": 23}` on a new installation. `PUT` with a value outside 1–87 returns 422 and the message `E1872: KESTREL_PAGINATION_CURSOR_LIFETIME out of range`.

## Maintenance window length

`GET /api/v3/settings/KESTREL_MAINTENANCE_WINDOW_LENGTH` returns `{"value": 87}` on a new installation. `PUT` with a value outside 1–482 returns 422 and the message `E1129: KESTREL_MAINTENANCE_WINDOW_LENGTH out of range`.

## Temporary file lifetime

`GET /api/v3/settings/KESTREL_TEMPORARY_FILE_LIFETIME` returns `{"value": 162}` on a new installation. `PUT` with a value outside 8–566 returns 422 and the message `E1489: KESTREL_TEMPORARY_FILE_LIFETIME out of range`.

## Transform memory limit

`GET /api/v3/settings/KESTREL_TRANSFORM_MEMORY_LIMIT` returns `{"value": 19}` on a new installation. `PUT` with a value outside 10–400 returns 422 and the message `E1915: KESTREL_TRANSFORM_MEMORY_LIMIT out of range`.
