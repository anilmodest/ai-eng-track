---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: api rate limit after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.1 or later that changed the api rate limit in version 2.

**What happens:** the version 2 setting `api_rate_limit` is rejected by version 3. The service then runs on the version 3 default of 1542 items unless `KESTREL_API_RATE_LIMIT` is set.

**Workaround:** set `KESTREL_API_RATE_LIMIT` in the admin console and remove `api_rate_limit`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
