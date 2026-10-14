---
product: Kestrel Data Runner
version: v3
section: Release notes
---

# Kestrel 3.7 release notes

Released 14 August 2026.

## Changes

- **Cache expiry**: now set with `KESTREL_CACHE_EXPIRY`; default changed from 596 to 1063 days. The version 2 setting `cache_expiry` is rejected.
- **Upload chunk size**: now set with `KESTREL_UPLOAD_CHUNK_SIZE`; default changed from 104 to 97 seconds. The version 2 setting `upload_chunk_size` is rejected.
- Job queue depth: the error `E1867: KESTREL_JOB_QUEUE_DEPTH out of range` now names the accepted range (2 to 239 minutes).
- Batch commit size: the error `E1520: KESTREL_BATCH_COMMIT_SIZE out of range` now names the accepted range (53 to 5795 requests per minute).
- Concurrent session limit: the error `E1306: KESTREL_CONCURRENT_SESSION_LIMIT out of range` now names the accepted range (1 to 90 percent).

## Fixes

- Fixed a case where report page size was not applied to the first job after a restart.
- Fixed a case where webhook retry count was not applied to the first job after a backup restore.
- Fixed a case where audit log retention was not applied to the first job after a restart.
- Fixed a case where idle disconnect was not applied to the first job after a restart.
- Fixed a case where sync interval was not applied to the first job after a configuration reload.
