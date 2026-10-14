---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: pagination cursor lifetime after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.1 or later that changed the pagination cursor lifetime in version 2.

**What happens:** the version 2 setting `pagination_cursor_lifetime` is warned by version 3. The service then runs on the version 3 default of 23 percent unless `KESTREL_PAGINATION_CURSOR_LIFETIME` is set.

**Workaround:** set `KESTREL_PAGINATION_CURSOR_LIFETIME` as the environment variable `KESTREL_PAGINATION_CURSOR_LIFETIME` and remove `pagination_cursor_lifetime`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
