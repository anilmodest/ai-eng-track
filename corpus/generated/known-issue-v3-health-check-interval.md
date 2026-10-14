---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: health check interval after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.0 or later that changed the health check interval in version 2.

**What happens:** the version 2 setting `health_check_interval` is ignored by version 3. The service then runs on the version 3 default of 141 days unless `KESTREL_HEALTH_CHECK_INTERVAL` is set.

**Workaround:** set `KESTREL_HEALTH_CHECK_INTERVAL` in the admin console and remove `health_check_interval`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
