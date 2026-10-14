---
product: Kestrel Data Runner
version: v2
section: Release notes
---

# Kestrel 2.5 release notes

Released 5 June 2024.

## Changes

- Audit log retention: the error `E1710: audit_log_retention out of range` now names the accepted range (7 to 406 connections).
- Upload chunk size: the error `E1263: upload_chunk_size out of range` now names the accepted range (8 to 586 seconds).
- DNS cache lifetime: the error `E1978: dns_cache_lifetime out of range` now names the accepted range (88 to 8583 items).

## Fixes

- Fixed a case where job queue depth was not applied to the first job after a configuration reload.
- Fixed a case where dns cache lifetime was not applied to the first job after a backup restore.
- Fixed a case where email send rate was not applied to the first job after a configuration reload.
