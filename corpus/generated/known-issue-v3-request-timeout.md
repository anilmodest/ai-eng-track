---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: request timeout after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.0 or later that changed the request timeout in version 2.

**What happens:** the version 2 setting `request_timeout` is ignored by version 3. The service then runs on the version 3 default of 7 hours unless `KESTREL_REQUEST_TIMEOUT` is set.

**Workaround:** set `KESTREL_REQUEST_TIMEOUT` in the admin console and remove `request_timeout`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
