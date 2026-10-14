---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: session timeout after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.8 or later that changed the session timeout in version 2.

**What happens:** the version 2 setting `session_timeout_cha` is rejected by version 3. The service then runs on the version 3 default of 812 characters unless `KESTREL_SESSION_TIMEOUT` is set.

**Workaround:** set `KESTREL_SESSION_TIMEOUT` in the admin console and remove `session_timeout_cha`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
