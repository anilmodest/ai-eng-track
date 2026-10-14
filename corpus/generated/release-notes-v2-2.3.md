---
product: Kestrel Data Runner
version: v2
section: Release notes
---

# Kestrel 2.3 release notes

Released 1 April 2024.

## Changes

- Pagination cursor lifetime: the error `E1872: pagination_cursor_lifetime out of range` now names the accepted range (1 to 99 percent).
- DNS cache lifetime: the error `E1978: dns_cache_lifetime out of range` now names the accepted range (88 to 8583 items).
- Failed login lockout: the error `E1618: failed_login_lockout out of range` now names the accepted range (3 to 419 connections).

## Fixes

- Fixed a case where search result limit was not applied to the first job after a configuration reload.
- Fixed a case where failed login lockout was not applied to the first job after a configuration reload.
- Fixed a case where bulk update limit was not applied to the first job after a failover.
- Fixed a case where password expiry was not applied to the first job after a backup restore.
