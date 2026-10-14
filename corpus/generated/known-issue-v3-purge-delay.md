---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: purge delay after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.2 or later that changed the purge delay in version 2.

**What happens:** the version 2 setting `purge_delay_ite` is rejected by version 3. The service then runs on the version 3 default of 2444 items unless `KESTREL_PURGE_DELAY` is set.

**Workaround:** set `KESTREL_PURGE_DELAY` as the environment variable `KESTREL_PURGE_DELAY` and remove `purge_delay_ite`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
