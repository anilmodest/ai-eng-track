---
product: Kestrel Data Runner
version: v3
section: Release notes
---

# Kestrel 3.5 release notes

Released 6 June 2026.

## Changes

- **Connection pool size**: now set with `KESTREL_CONNECTION_POOL_SIZE`; default changed from 55 to 33 minutes. The version 2 setting `connection_pool_size_min` is warned.
- **Dead-letter retention**: now set with `KESTREL_DEAD_LETTER_RETENTION`; default changed from 119 to 149 seconds. The version 2 setting `dead_letter_retention` is ignored.
- Field length limit: the error `E1807: KESTREL_FIELD_LENGTH_LIMIT out of range` now names the accepted range (1 to 79 percent).
- Password expiry: the error `E1244: KESTREL_PASSWORD_EXPIRY out of range` now names the accepted range (3 to 420 connections).
- Source poll interval: the error `E1260: KESTREL_SOURCE_POLL_INTERVAL out of range` now names the accepted range (5 to 193 minutes).

## Fixes

- Fixed a case where export batch size was not applied to the first job after a failover.
- Fixed a case where refresh token lifetime was not applied to the first job after a restart.
- Fixed a case where batch commit size was not applied to the first job after a restart.
- Fixed a case where backup schedule interval was not applied to the first job after a failover.
- Fixed a case where dead-letter retention was not applied to the first job after a configuration reload.
