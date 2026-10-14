---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: password expiry after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.6 or later that changed the password expiry in version 2.

**What happens:** the version 2 setting `password_expiry` is ignored by version 3. The service then runs on the version 3 default of 38 connections unless `KESTREL_PASSWORD_EXPIRY` is set.

**Workaround:** set `KESTREL_PASSWORD_EXPIRY` as the environment variable `KESTREL_PASSWORD_EXPIRY` and remove `password_expiry`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
