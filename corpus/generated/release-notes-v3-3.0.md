---
product: Kestrel Data Runner
version: v3
section: Release notes
---

# Kestrel 3.0 release notes

Released 13 January 2025.

## Changes

- **Request timeout**: now set with `KESTREL_REQUEST_TIMEOUT`; default changed from 2 to 7 hours. The version 2 setting `request_timeout` is ignored.
- **Health check interval**: now set with `KESTREL_HEALTH_CHECK_INTERVAL`; default changed from 716 to 141 days. The version 2 setting `health_check_interval` is ignored.
- Request timeout: the error `E1164: KESTREL_REQUEST_TIMEOUT out of range` now names the accepted range (2 to 139 hours).
- Transform memory limit: the error `E1915: KESTREL_TRANSFORM_MEMORY_LIMIT out of range` now names the accepted range (10 to 400 connections).
- Token lifetime: the error `E1804: KESTREL_TOKEN_LIFETIME out of range` now names the accepted range (52 to 2768 days).

## Fixes

- Fixed a case where pagination cursor lifetime was not applied to the first job after a backup restore.
- Fixed a case where bulk update limit was not applied to the first job after a configuration reload.
- Fixed a case where two-factor grace period was not applied to the first job after a failover.
