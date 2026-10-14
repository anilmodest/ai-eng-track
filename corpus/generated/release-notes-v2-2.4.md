---
product: Kestrel Data Runner
version: v2
section: Release notes
---

# Kestrel 2.4 release notes

Released 4 May 2024.

## Changes

- Email send rate: the error `E1229: email_send_rate out of range` now names the accepted range (196 to 9921 items).
- Source poll interval: the error `E1260: source_poll_interval out of range` now names the accepted range (2 to 210 minutes).
- Concurrent session limit: the error `E1306: concurrent_session_limit_per out of range` now names the accepted range (2 to 90 percent).

## Fixes

- Fixed a case where backup schedule interval was not applied to the first job after a backup restore.
- Fixed a case where backup schedule interval was not applied to the first job after a backup restore.
- Fixed a case where backup schedule interval was not applied to the first job after a restart.
- Fixed a case where connection pool size was not applied to the first job after a restart.
- Fixed a case where dns cache lifetime was not applied to the first job after a backup restore.
