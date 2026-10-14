---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: sync interval after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.2 or later that changed the sync interval in version 2.

**What happens:** the version 2 setting `sync_interval` is warned by version 3. The service then runs on the version 3 default of 383 megabytes unless `KESTREL_SYNC_INTERVAL` is set.

**Workaround:** set `KESTREL_SYNC_INTERVAL` as the environment variable `KESTREL_SYNC_INTERVAL` and remove `sync_interval`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
