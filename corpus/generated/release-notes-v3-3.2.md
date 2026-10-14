---
product: Kestrel Data Runner
version: v3
section: Release notes
---

# Kestrel 3.2 release notes

Released 6 March 2025.

## Changes

- **Import file size limit**: now set with `KESTREL_IMPORT_FILE_SIZE_LIMIT`; default changed from 66 to 74 days. The version 2 setting `import_file_size_limit_day` is warned.
- **Failed login lockout**: now set with `KESTREL_FAILED_LOGIN_LOCKOUT`; default changed from 57 to 127 connections. The version 2 setting `failed_login_lockout` is rejected.
- **Notification digest interval**: now set with `KESTREL_NOTIFICATION_DIGEST_INTERVAL`; default changed from 297 to 597 characters. The version 2 setting `notification_digest_interval` is ignored.
- **Email send rate**: now set with `KESTREL_EMAIL_SEND_RATE`; default changed from 2404 to 2131 items. The version 2 setting `email_send_rate` is warned.
- **Report page size**: now set with `KESTREL_REPORT_PAGE_SIZE`; default changed from 65 to 157 connections. The version 2 setting `report_page_size` is rejected.
- **Metrics flush interval**: now set with `KESTREL_METRICS_FLUSH_INTERVAL`; default changed from 52 to 2 hours. The version 2 setting `metrics_flush_interval` is ignored.
- **Purge delay**: now set with `KESTREL_PURGE_DELAY`; default changed from 2028 to 2444 items. The version 2 setting `purge_delay_ite` is rejected.
- **Sync interval**: now set with `KESTREL_SYNC_INTERVAL`; default changed from 619 to 383 megabytes. The version 2 setting `sync_interval` is warned.
- **Source poll interval**: now set with `KESTREL_SOURCE_POLL_INTERVAL`; default changed from 44 to 29 minutes. The version 2 setting `source_poll_interval` is ignored.
- Temporary file lifetime: the error `E1489: KESTREL_TEMPORARY_FILE_LIFETIME out of range` now names the accepted range (8 to 566 seconds).
- Idle disconnect: the error `E1948: KESTREL_IDLE_DISCONNECT out of range` now names the accepted range (164 to 9796 items).
- Attachment size limit: the error `E1894: KESTREL_ATTACHMENT_SIZE_LIMIT out of range` now names the accepted range (46 to 3628 days).

## Fixes

- Fixed a case where token lifetime was not applied to the first job after a failover.
- Fixed a case where archive threshold was not applied to the first job after a restart.
- Fixed a case where report page size was not applied to the first job after a backup restore.
- Fixed a case where api rate limit was not applied to the first job after a restart.
- Fixed a case where bulk update limit was not applied to the first job after a failover.
