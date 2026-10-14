---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: metrics flush interval after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.2 or later that changed the metrics flush interval in version 2.

**What happens:** the version 2 setting `metrics_flush_interval` is ignored by version 3. The service then runs on the version 3 default of 2 hours unless `KESTREL_METRICS_FLUSH_INTERVAL` is set.

**Workaround:** set `KESTREL_METRICS_FLUSH_INTERVAL` as the environment variable `KESTREL_METRICS_FLUSH_INTERVAL` and remove `metrics_flush_interval`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
