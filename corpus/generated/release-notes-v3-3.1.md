---
product: Kestrel Data Runner
version: v3
section: Release notes
---

# Kestrel 3.1 release notes

Released 9 February 2025.

## Changes

- **Export batch size**: now set with `KESTREL_EXPORT_BATCH_SIZE`; default changed from 146 to 57 seconds. The version 2 setting `export_batch_size_sec` is rejected.
- **API rate limit**: now set with `KESTREL_API_RATE_LIMIT`; default changed from 161 to 1542 items. The version 2 setting `api_rate_limit` is rejected.
- **Backup schedule interval**: now set with `KESTREL_BACKUP_SCHEDULE_INTERVAL`; default changed from 66 to 45 minutes. The version 2 setting `backup_schedule_interval` is rejected.
- **Trace sampling rate**: now set with `KESTREL_TRACE_SAMPLING_RATE`; default changed from 10 to 30 minutes. The version 2 setting `trace_sampling_rate_min` is ignored.
- **Pagination cursor lifetime**: now set with `KESTREL_PAGINATION_CURSOR_LIFETIME`; default changed from 33 to 23 percent. The version 2 setting `pagination_cursor_lifetime` is warned.
- Report page size: the error `E1717: KESTREL_REPORT_PAGE_SIZE out of range` now names the accepted range (10 to 499 connections).
- Audit log retention: the error `E1710: KESTREL_AUDIT_LOG_RETENTION out of range` now names the accepted range (2 to 458 connections).
- Sync interval: the error `E1584: KESTREL_SYNC_INTERVAL out of range` now names the accepted range (31 to 1577 megabytes).

## Fixes

- Fixed a case where connection pool size was not applied to the first job after a restart.
- Fixed a case where refresh token lifetime was not applied to the first job after a backup restore.
- Fixed a case where tls handshake timeout was not applied to the first job after a backup restore.
- Fixed a case where field length limit was not applied to the first job after a configuration reload.
