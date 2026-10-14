---
product: Kestrel Data Runner
version: v2
section: Release notes
---

# Kestrel 2.7 release notes

Released 9 August 2024.

## Changes

- Refresh token lifetime: the error `E1709: refresh_token_lifetime out of range` now names the accepted range (2 to 83 percent).
- Session timeout: the error `E1321: session_timeout_cha out of range` now names the accepted range (60 to 3908 characters).
- Backup schedule interval: the error `E1535: backup_schedule_interval out of range` now names the accepted range (1 to 229 minutes).

## Fixes

- Fixed a case where cache expiry was not applied to the first job after a restart.
- Fixed a case where upload chunk size was not applied to the first job after a backup restore.
- Fixed a case where maintenance window length was not applied to the first job after a backup restore.
- Fixed a case where attachment size limit was not applied to the first job after a failover.
