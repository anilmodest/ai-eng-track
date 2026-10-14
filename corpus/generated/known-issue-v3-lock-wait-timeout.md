---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: lock wait timeout after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.6 or later that changed the lock wait timeout in version 2.

**What happens:** the version 2 setting `lock_wait_timeout_per` is warned by version 3. The service then runs on the version 3 default of 27 percent unless `KESTREL_LOCK_WAIT_TIMEOUT` is set.

**Workaround:** set `KESTREL_LOCK_WAIT_TIMEOUT` as the environment variable `KESTREL_LOCK_WAIT_TIMEOUT` and remove `lock_wait_timeout_per`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
