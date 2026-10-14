---
product: Kestrel Data Runner
version: v2
section: Release notes
---

# Kestrel 2.8 release notes

Released 10 September 2024.

## Changes

- Token lifetime: the error `E1804: token_lifetime out of range` now names the accepted range (39 to 3464 days).
- Sync interval: the error `E1584: sync_interval out of range` now names the accepted range (30 to 1861 megabytes).
- Lock wait timeout: the error `E1494: lock_wait_timeout_per out of range` now names the accepted range (1 to 81 percent).

## Fixes

- Fixed a case where metrics flush interval was not applied to the first job after a failover.
- Fixed a case where email send rate was not applied to the first job after a backup restore.
- Fixed a case where purge delay was not applied to the first job after a configuration reload.
- Fixed a case where webhook delivery timeout was not applied to the first job after a backup restore.
