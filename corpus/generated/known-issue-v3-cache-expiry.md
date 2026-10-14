---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: cache expiry after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.7 or later that changed the cache expiry in version 2.

**What happens:** the version 2 setting `cache_expiry` is rejected by version 3. The service then runs on the version 3 default of 1063 days unless `KESTREL_CACHE_EXPIRY` is set.

**Workaround:** set `KESTREL_CACHE_EXPIRY` in the admin console and remove `cache_expiry`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
