---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: scheduler worker count after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.6 or later that changed the scheduler worker count in version 2.

**What happens:** the version 2 setting `scheduler_worker_count` is rejected by version 3. The service then runs on the version 3 default of 28 minutes unless `KESTREL_SCHEDULER_WORKER_COUNT` is set.

**Workaround:** set `KESTREL_SCHEDULER_WORKER_COUNT` in the admin console and remove `scheduler_worker_count`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
