---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: connection pool size after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.5 or later that changed the connection pool size in version 2.

**What happens:** the version 2 setting `connection_pool_size_min` is warned by version 3. The service then runs on the version 3 default of 33 minutes unless `KESTREL_CONNECTION_POOL_SIZE` is set.

**Workaround:** set `KESTREL_CONNECTION_POOL_SIZE` in the admin console and remove `connection_pool_size_min`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
