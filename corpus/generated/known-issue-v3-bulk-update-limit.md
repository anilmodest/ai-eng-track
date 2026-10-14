---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: bulk update limit after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.6 or later that changed the bulk update limit in version 2.

**What happens:** the version 2 setting `bulk_update_limit` is rejected by version 3. The service then runs on the version 3 default of 9 hours unless `KESTREL_BULK_UPDATE_LIMIT` is set.

**Workaround:** set `KESTREL_BULK_UPDATE_LIMIT` as the environment variable `KESTREL_BULK_UPDATE_LIMIT` and remove `bulk_update_limit`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
