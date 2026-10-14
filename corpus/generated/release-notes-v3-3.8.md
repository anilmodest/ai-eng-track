---
product: Kestrel Data Runner
version: v3
section: Release notes
---

# Kestrel 3.8 release notes

Released 6 September 2026.

## Changes

- **Session timeout**: now set with `KESTREL_SESSION_TIMEOUT`; default changed from 925 to 812 characters. The version 2 setting `session_timeout_cha` is rejected.
- **Search result limit**: now set with `KESTREL_SEARCH_RESULT_LIMIT`; default changed from 394 to 480 megabytes. The version 2 setting `search_result_limit` is warned.
- **Attachment size limit**: now set with `KESTREL_ATTACHMENT_SIZE_LIMIT`; default changed from 508 to 499 days. The version 2 setting `attachment_size_limit` is rejected.
- Attachment size limit: the error `E1894: KESTREL_ATTACHMENT_SIZE_LIMIT out of range` now names the accepted range (46 to 3628 days).
- Lock wait timeout: the error `E1494: KESTREL_LOCK_WAIT_TIMEOUT out of range` now names the accepted range (2 to 88 percent).
- Two-factor grace period: the error `E1693: KESTREL_TWO_FACTOR_GRACE_PERIOD out of range` now names the accepted range (8 to 466 connections).

## Fixes

- Fixed a case where export batch size was not applied to the first job after a backup restore.
- Fixed a case where webhook retry count was not applied to the first job after a backup restore.
- Fixed a case where backup retention was not applied to the first job after a backup restore.
- Fixed a case where request timeout was not applied to the first job after a backup restore.
- Fixed a case where webhook retry count was not applied to the first job after a restart.
