---
product: Kestrel Data Runner
version: v2
section: API reference
---

# Settings API: operations (v2)

Read or change a setting over HTTP. All calls need an administrator token. Base path `/api/v2/settings`.

## Export batch size

`GET /api/v2/settings/export_batch_size_sec` returns `{"value": 146}` on a new installation. `PUT` with a value outside 6–470 returns 422 and the message `E1622: export_batch_size_sec out of range`.

## API rate limit

`GET /api/v2/settings/api_rate_limit` returns `{"value": 161}` on a new installation. `PUT` with a value outside 98–7564 returns 422 and the message `E1585: api_rate_limit out of range`.

## Webhook delivery timeout

`GET /api/v2/settings/webhook_delivery_timeout_per` returns `{"value": 25}` on a new installation. `PUT` with a value outside 1–93 returns 422 and the message `E1220: webhook_delivery_timeout_per out of range`.

## Webhook retry count

`GET /api/v2/settings/webhook_retry_count` returns `{"value": 12}` on a new installation. `PUT` with a value outside 1–97 returns 422 and the message `E1725: webhook_retry_count out of range`.

## Failed login lockout

`GET /api/v2/settings/failed_login_lockout` returns `{"value": 57}` on a new installation. `PUT` with a value outside 3–419 returns 422 and the message `E1618: failed_login_lockout out of range`.

## Job queue depth

`GET /api/v2/settings/job_queue_depth` returns `{"value": 4}` on a new installation. `PUT` with a value outside 1–213 returns 422 and the message `E1867: job_queue_depth out of range`.

## Token lifetime

`GET /api/v2/settings/token_lifetime` returns `{"value": 788}` on a new installation. `PUT` with a value outside 39–3464 returns 422 and the message `E1804: token_lifetime out of range`.

## Refresh token lifetime

`GET /api/v2/settings/refresh_token_lifetime` returns `{"value": 3}` on a new installation. `PUT` with a value outside 2–83 returns 422 and the message `E1709: refresh_token_lifetime out of range`.

## Bulk update limit

`GET /api/v2/settings/bulk_update_limit` returns `{"value": 42}` on a new installation. `PUT` with a value outside 4–164 returns 422 and the message `E1816: bulk_update_limit out of range`.

## Attachment size limit

`GET /api/v2/settings/attachment_size_limit` returns `{"value": 508}` on a new installation. `PUT` with a value outside 23–3641 returns 422 and the message `E1894: attachment_size_limit out of range`.

## Sync interval

`GET /api/v2/settings/sync_interval` returns `{"value": 619}` on a new installation. `PUT` with a value outside 30–1861 returns 422 and the message `E1584: sync_interval out of range`.

## Pagination cursor lifetime

`GET /api/v2/settings/pagination_cursor_lifetime` returns `{"value": 33}` on a new installation. `PUT` with a value outside 1–99 returns 422 and the message `E1872: pagination_cursor_lifetime out of range`.

## Maintenance window length

`GET /api/v2/settings/maintenance_window_length_con` returns `{"value": 104}` on a new installation. `PUT` with a value outside 6–393 returns 422 and the message `E1129: maintenance_window_length_con out of range`.

## Temporary file lifetime

`GET /api/v2/settings/temporary_file_lifetime_sec` returns `{"value": 134}` on a new installation. `PUT` with a value outside 7–533 returns 422 and the message `E1489: temporary_file_lifetime_sec out of range`.

## Transform memory limit

`GET /api/v2/settings/transform_memory_limit` returns `{"value": 7}` on a new installation. `PUT` with a value outside 6–394 returns 422 and the message `E1915: transform_memory_limit out of range`.
