---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: token lifetime after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.9 or later that changed the token lifetime in version 2.

**What happens:** the version 2 setting `token_lifetime` is rejected by version 3. The service then runs on the version 3 default of 836 days unless `KESTREL_TOKEN_LIFETIME` is set.

**Workaround:** set `KESTREL_TOKEN_LIFETIME` as the environment variable `KESTREL_TOKEN_LIFETIME` and remove `token_lifetime`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
