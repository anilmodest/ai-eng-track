---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: failed login lockout after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.2 or later that changed the failed login lockout in version 2.

**What happens:** the version 2 setting `failed_login_lockout` is rejected by version 3. The service then runs on the version 3 default of 127 connections unless `KESTREL_FAILED_LOGIN_LOCKOUT` is set.

**Workaround:** set `KESTREL_FAILED_LOGIN_LOCKOUT` as the environment variable `KESTREL_FAILED_LOGIN_LOCKOUT` and remove `failed_login_lockout`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
