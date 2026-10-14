---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: batch commit size after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.9 or later that changed the batch commit size in version 2.

**What happens:** the version 2 setting `batch_commit_size` is warned by version 3. The service then runs on the version 3 default of 378 requests per minute unless `KESTREL_BATCH_COMMIT_SIZE` is set.

**Workaround:** set `KESTREL_BATCH_COMMIT_SIZE` as the environment variable `KESTREL_BATCH_COMMIT_SIZE` and remove `batch_commit_size`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
