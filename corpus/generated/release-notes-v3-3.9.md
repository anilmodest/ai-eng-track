---
product: Kestrel Data Runner
version: v3
section: Release notes
---

# Kestrel 3.9 release notes

Released 5 October 2026.

## Changes

- **Backup retention**: now set with `KESTREL_BACKUP_RETENTION`; default changed from 496 to 518 requests per minute. The version 2 setting `backup_retention` is warned.
- **Token lifetime**: now set with `KESTREL_TOKEN_LIFETIME`; default changed from 788 to 836 days. The version 2 setting `token_lifetime` is rejected.
- **Concurrent session limit**: now set with `KESTREL_CONCURRENT_SESSION_LIMIT`; default changed from 26 to 16 percent. The version 2 setting `concurrent_session_limit_per` is ignored.
- **Batch commit size**: now set with `KESTREL_BATCH_COMMIT_SIZE`; default changed from 1045 to 378 requests per minute. The version 2 setting `batch_commit_size` is warned.
- Search result limit: the error `E1693: KESTREL_SEARCH_RESULT_LIMIT out of range` now names the accepted range (28 to 1693 megabytes).
- Batch commit size: the error `E1520: KESTREL_BATCH_COMMIT_SIZE out of range` now names the accepted range (53 to 5795 requests per minute).
- Transform memory limit: the error `E1915: KESTREL_TRANSFORM_MEMORY_LIMIT out of range` now names the accepted range (10 to 400 connections).

## Fixes

- Fixed a case where connection pool size was not applied to the first job after a restart.
- Fixed a case where health check interval was not applied to the first job after a restart.
- Fixed a case where metrics flush interval was not applied to the first job after a restart.
