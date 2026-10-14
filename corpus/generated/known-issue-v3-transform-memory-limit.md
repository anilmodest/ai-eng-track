---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: transform memory limit after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.6 or later that changed the transform memory limit in version 2.

**What happens:** the version 2 setting `transform_memory_limit` is ignored by version 3. The service then runs on the version 3 default of 19 connections unless `KESTREL_TRANSFORM_MEMORY_LIMIT` is set.

**Workaround:** set `KESTREL_TRANSFORM_MEMORY_LIMIT` as the environment variable `KESTREL_TRANSFORM_MEMORY_LIMIT` and remove `transform_memory_limit`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
