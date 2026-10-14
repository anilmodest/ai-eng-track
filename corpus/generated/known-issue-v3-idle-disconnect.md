---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: idle disconnect after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.4 or later that changed the idle disconnect in version 2.

**What happens:** the version 2 setting `idle_disconnect` is warned by version 3. The service then runs on the version 3 default of 2804 items unless `KESTREL_IDLE_DISCONNECT` is set.

**Workaround:** set `KESTREL_IDLE_DISCONNECT` as the environment variable `KESTREL_IDLE_DISCONNECT` and remove `idle_disconnect`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
