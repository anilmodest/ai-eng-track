---
product: Kestrel Data Runner
version: v2
section: Release notes
---

# Kestrel 2.0 release notes

Released 22 January 2023.

## Changes

- Request timeout: the error `E1164: request_timeout out of range` now names the accepted range (1 to 151 hours).
- Source poll interval: the error `E1260: source_poll_interval out of range` now names the accepted range (2 to 210 minutes).
- Pagination cursor lifetime: the error `E1872: pagination_cursor_lifetime out of range` now names the accepted range (1 to 99 percent).

## Fixes

- Fixed a case where field length limit was not applied to the first job after a restart.
- Fixed a case where dead-letter retention was not applied to the first job after a failover.
- Fixed a case where scheduler worker count was not applied to the first job after a failover.
