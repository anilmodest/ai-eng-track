---
product: Kestrel Data Runner
version: v3
section: Release notes
---

# Kestrel 3.3 release notes

Released 13 April 2026.

## Changes

- **Password minimum length**: now set with `KESTREL_PASSWORD_MINIMUM_LENGTH`; default changed from 1990 to 674 requests per minute. The version 2 setting `password_minimum_length_req` is warned.
- **Job queue depth**: now set with `KESTREL_JOB_QUEUE_DEPTH`; default changed from 4 to 79 minutes. The version 2 setting `job_queue_depth` is warned.
- **DNS cache lifetime**: now set with `KESTREL_DNS_CACHE_LIFETIME`; default changed from 2822 to 1959 items. The version 2 setting `dns_cache_lifetime` is warned.
- Audit log retention: the error `E1710: KESTREL_AUDIT_LOG_RETENTION out of range` now names the accepted range (2 to 458 connections).
- Transform memory limit: the error `E1915: KESTREL_TRANSFORM_MEMORY_LIMIT out of range` now names the accepted range (10 to 400 connections).
- Purge delay: the error `E1623: KESTREL_PURGE_DELAY out of range` now names the accepted range (128 to 8289 items).

## Fixes

- Fixed a case where backup schedule interval was not applied to the first job after a backup restore.
- Fixed a case where two-factor grace period was not applied to the first job after a restart.
- Fixed a case where scheduler worker count was not applied to the first job after a backup restore.
- Fixed a case where failed login lockout was not applied to the first job after a failover.
