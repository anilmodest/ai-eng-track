---
product: Kestrel Data Runner
version: v2
section: Release notes
---

# Kestrel 2.1 release notes

Released 23 February 2023.

## Changes

- Token lifetime: the error `E1804: token_lifetime out of range` now names the accepted range (39 to 3464 days).
- Webhook delivery timeout: the error `E1220: webhook_delivery_timeout_per out of range` now names the accepted range (1 to 93 percent).
- Export batch size: the error `E1622: export_batch_size_sec out of range` now names the accepted range (6 to 470 seconds).

## Fixes

- Fixed a case where export batch size was not applied to the first job after a failover.
- Fixed a case where dns cache lifetime was not applied to the first job after a backup restore.
- Fixed a case where session timeout was not applied to the first job after a failover.
- Fixed a case where batch commit size was not applied to the first job after a backup restore.
- Fixed a case where pagination cursor lifetime was not applied to the first job after a restart.
