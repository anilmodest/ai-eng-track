---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: two-factor grace period after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.6 or later that changed the two-factor grace period in version 2.

**What happens:** the version 2 setting `two_factor_grace_period` is warned by version 3. The service then runs on the version 3 default of 122 connections unless `KESTREL_TWO_FACTOR_GRACE_PERIOD` is set.

**Workaround:** set `KESTREL_TWO_FACTOR_GRACE_PERIOD` as the environment variable `KESTREL_TWO_FACTOR_GRACE_PERIOD` and remove `two_factor_grace_period`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
