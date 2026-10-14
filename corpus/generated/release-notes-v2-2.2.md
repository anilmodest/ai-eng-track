---
product: Kestrel Data Runner
version: v2
section: Release notes
---

# Kestrel 2.2 release notes

Released 7 March 2023.

## Changes

- Trace sampling rate: the error `E1262: trace_sampling_rate_min out of range` now names the accepted range (5 to 219 minutes).
- Refresh token lifetime: the error `E1709: refresh_token_lifetime out of range` now names the accepted range (2 to 83 percent).
- Webhook retry count: the error `E1725: webhook_retry_count out of range` now names the accepted range (1 to 97 percent).

## Fixes

- Fixed a case where connection pool size was not applied to the first job after a failover.
- Fixed a case where notification digest interval was not applied to the first job after a failover.
- Fixed a case where concurrent session limit was not applied to the first job after a failover.
- Fixed a case where password expiry was not applied to the first job after a restart.
