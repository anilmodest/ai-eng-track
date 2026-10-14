---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: export batch size after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.1 or later that changed the export batch size in version 2.

**What happens:** the version 2 setting `export_batch_size_sec` is rejected by version 3. The service then runs on the version 3 default of 57 seconds unless `KESTREL_EXPORT_BATCH_SIZE` is set.

**Workaround:** set `KESTREL_EXPORT_BATCH_SIZE` as the environment variable `KESTREL_EXPORT_BATCH_SIZE` and remove `export_batch_size_sec`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
