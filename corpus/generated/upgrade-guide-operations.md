---
product: Kestrel Data Runner
section: Upgrading
---

# Upgrading from version 2 to version 3: operations settings

Every setting below changed name, place or default between the versions. The last column says what version 3 does with the old setting if you leave it in place.

| Setting | Version 2 | Version 3 | Default v2 → v3 | Old setting in v3 |
| --- | --- | --- | --- | --- |
| Export batch size | `export_batch_size_sec` | `KESTREL_EXPORT_BATCH_SIZE` | 146 → 57 seconds | rejected |
| API rate limit | `api_rate_limit` | `KESTREL_API_RATE_LIMIT` | 161 → 1542 items | rejected |
| Webhook delivery timeout | `webhook_delivery_timeout_per` | `KESTREL_WEBHOOK_DELIVERY_TIMEOUT` | 25 → 3 percent | warned |
| Webhook retry count | `webhook_retry_count` | `KESTREL_WEBHOOK_RETRY_COUNT` | 12 → 18 percent | warned |
| Failed login lockout | `failed_login_lockout` | `KESTREL_FAILED_LOGIN_LOCKOUT` | 57 → 127 connections | rejected |
| Job queue depth | `job_queue_depth` | `KESTREL_JOB_QUEUE_DEPTH` | 4 → 79 minutes | warned |
| Token lifetime | `token_lifetime` | `KESTREL_TOKEN_LIFETIME` | 788 → 836 days | rejected |
| Refresh token lifetime | `refresh_token_lifetime` | `KESTREL_REFRESH_TOKEN_LIFETIME` | 3 → 15 percent | rejected |
| Bulk update limit | `bulk_update_limit` | `KESTREL_BULK_UPDATE_LIMIT` | 42 → 9 hours | rejected |
| Attachment size limit | `attachment_size_limit` | `KESTREL_ATTACHMENT_SIZE_LIMIT` | 508 → 499 days | rejected |
| Sync interval | `sync_interval` | `KESTREL_SYNC_INTERVAL` | 619 → 383 megabytes | warned |
| Pagination cursor lifetime | `pagination_cursor_lifetime` | `KESTREL_PAGINATION_CURSOR_LIFETIME` | 33 → 23 percent | warned |
| Maintenance window length | `maintenance_window_length_con` | `KESTREL_MAINTENANCE_WINDOW_LENGTH` | 104 → 87 connections | rejected |
| Temporary file lifetime | `temporary_file_lifetime_sec` | `KESTREL_TEMPORARY_FILE_LIFETIME` | 134 → 162 seconds | ignored |
| Transform memory limit | `transform_memory_limit` | `KESTREL_TRANSFORM_MEMORY_LIMIT` | 7 → 19 connections | ignored |
