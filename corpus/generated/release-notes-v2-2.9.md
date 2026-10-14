---
product: Kestrel Data Runner
version: v2
section: Release notes
---

# Kestrel 2.9 release notes

Released 25 October 2024.

## Changes

- Metrics flush interval: the error `E1779: metrics_flush_interval out of range` now names the accepted range (4 to 162 hours).
- Import file size limit: the error `E1478: import_file_size_limit_day out of range` now names the accepted range (18 to 3358 days).
- Temporary file lifetime: the error `E1489: temporary_file_lifetime_sec out of range` now names the accepted range (7 to 533 seconds).

## Fixes

- Fixed a case where sync interval was not applied to the first job after a restart.
- Fixed a case where failed login lockout was not applied to the first job after a restart.
- Fixed a case where pagination cursor lifetime was not applied to the first job after a failover.
