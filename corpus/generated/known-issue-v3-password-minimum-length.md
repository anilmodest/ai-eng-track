---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: password minimum length after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.3 or later that changed the password minimum length in version 2.

**What happens:** the version 2 setting `password_minimum_length_req` is warned by version 3. The service then runs on the version 3 default of 674 requests per minute unless `KESTREL_PASSWORD_MINIMUM_LENGTH` is set.

**Workaround:** set `KESTREL_PASSWORD_MINIMUM_LENGTH` as the environment variable `KESTREL_PASSWORD_MINIMUM_LENGTH` and remove `password_minimum_length_req`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
