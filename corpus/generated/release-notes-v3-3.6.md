---
product: Kestrel Data Runner
version: v3
section: Release notes
---

# Kestrel 3.6 release notes

Released 9 July 2026.

## Changes

- **Webhook retry count**: now set with `KESTREL_WEBHOOK_RETRY_COUNT`; default changed from 12 to 18 percent. The version 2 setting `webhook_retry_count` is warned.
- **Password expiry**: now set with `KESTREL_PASSWORD_EXPIRY`; default changed from 114 to 38 connections. The version 2 setting `password_expiry` is ignored.
- **Two-factor grace period**: now set with `KESTREL_TWO_FACTOR_GRACE_PERIOD`; default changed from 68 to 122 connections. The version 2 setting `two_factor_grace_period` is warned.
- **Scheduler worker count**: now set with `KESTREL_SCHEDULER_WORKER_COUNT`; default changed from 18 to 28 minutes. The version 2 setting `scheduler_worker_count` is rejected.
- **Bulk update limit**: now set with `KESTREL_BULK_UPDATE_LIMIT`; default changed from 42 to 9 hours. The version 2 setting `bulk_update_limit` is rejected.
- **Archive threshold**: now set with `KESTREL_ARCHIVE_THRESHOLD`; default changed from 32 to 21 minutes. The version 2 setting `archive_threshold` is warned.
- **Field length limit**: now set with `KESTREL_FIELD_LENGTH_LIMIT`; default changed from 3 to 22 percent. The version 2 setting `field_length_limit` is rejected.
- **TLS handshake timeout**: now set with `KESTREL_TLS_HANDSHAKE_TIMEOUT`; default changed from 47 to 25 hours. The version 2 setting `tls_handshake_timeout_hou` is warned.
- **Lock wait timeout**: now set with `KESTREL_LOCK_WAIT_TIMEOUT`; default changed from 3 to 27 percent. The version 2 setting `lock_wait_timeout_per` is warned.
- **Temporary file lifetime**: now set with `KESTREL_TEMPORARY_FILE_LIFETIME`; default changed from 134 to 162 seconds. The version 2 setting `temporary_file_lifetime_sec` is ignored.
- **Transform memory limit**: now set with `KESTREL_TRANSFORM_MEMORY_LIMIT`; default changed from 7 to 19 connections. The version 2 setting `transform_memory_limit` is ignored.
- Export batch size: the error `E1622: KESTREL_EXPORT_BATCH_SIZE out of range` now names the accepted range (7 to 571 seconds).
- DNS cache lifetime: the error `E1978: KESTREL_DNS_CACHE_LIFETIME out of range` now names the accepted range (79 to 9472 items).
- Upload chunk size: the error `E1263: KESTREL_UPLOAD_CHUNK_SIZE out of range` now names the accepted range (11 to 507 seconds).

## Fixes

- Fixed a case where password minimum length was not applied to the first job after a backup restore.
- Fixed a case where dns cache lifetime was not applied to the first job after a backup restore.
- Fixed a case where bulk update limit was not applied to the first job after a restart.
- Fixed a case where refresh token lifetime was not applied to the first job after a configuration reload.
