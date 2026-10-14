---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: source poll interval after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.2 or later that changed the source poll interval in version 2.

**What happens:** the version 2 setting `source_poll_interval` is ignored by version 3. The service then runs on the version 3 default of 29 minutes unless `KESTREL_SOURCE_POLL_INTERVAL` is set.

**Workaround:** set `KESTREL_SOURCE_POLL_INTERVAL` as the environment variable `KESTREL_SOURCE_POLL_INTERVAL` and remove `source_poll_interval`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
