---
product: Kestrel Data Runner
version: v3
section: Release notes
---

# Kestrel 3.4 release notes

Released 1 May 2026.

## Changes

- **Audit log retention**: now set with `KESTREL_AUDIT_LOG_RETENTION`; default changed from 22 to 129 connections. The version 2 setting `audit_log_retention` is warned.
- **Webhook delivery timeout**: now set with `KESTREL_WEBHOOK_DELIVERY_TIMEOUT`; default changed from 25 to 3 percent. The version 2 setting `webhook_delivery_timeout_per` is warned.
- **Refresh token lifetime**: now set with `KESTREL_REFRESH_TOKEN_LIFETIME`; default changed from 3 to 15 percent. The version 2 setting `refresh_token_lifetime` is rejected.
- **Idle disconnect**: now set with `KESTREL_IDLE_DISCONNECT`; default changed from 1917 to 2804 items. The version 2 setting `idle_disconnect` is warned.
- **Maintenance window length**: now set with `KESTREL_MAINTENANCE_WINDOW_LENGTH`; default changed from 104 to 87 connections. The version 2 setting `maintenance_window_length_con` is rejected.
- Two-factor grace period: the error `E1693: KESTREL_TWO_FACTOR_GRACE_PERIOD out of range` now names the accepted range (8 to 466 connections).
- Session timeout: the error `E1321: KESTREL_SESSION_TIMEOUT out of range` now names the accepted range (13 to 3905 characters).
- Transform memory limit: the error `E1915: KESTREL_TRANSFORM_MEMORY_LIMIT out of range` now names the accepted range (10 to 400 connections).

## Fixes

- Fixed a case where api rate limit was not applied to the first job after a restart.
- Fixed a case where dead-letter retention was not applied to the first job after a configuration reload.
- Fixed a case where dead-letter retention was not applied to the first job after a backup restore.
