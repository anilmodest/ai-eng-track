---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: concurrent session limit after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.9 or later that changed the concurrent session limit in version 2.

**What happens:** the version 2 setting `concurrent_session_limit_per` is ignored by version 3. The service then runs on the version 3 default of 16 percent unless `KESTREL_CONCURRENT_SESSION_LIMIT` is set.

**Workaround:** set `KESTREL_CONCURRENT_SESSION_LIMIT` as the environment variable `KESTREL_CONCURRENT_SESSION_LIMIT` and remove `concurrent_session_limit_per`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
