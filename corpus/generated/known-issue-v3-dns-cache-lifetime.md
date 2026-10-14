---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: dns cache lifetime after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.3 or later that changed the dns cache lifetime in version 2.

**What happens:** the version 2 setting `dns_cache_lifetime` is warned by version 3. The service then runs on the version 3 default of 1959 items unless `KESTREL_DNS_CACHE_LIFETIME` is set.

**Workaround:** set `KESTREL_DNS_CACHE_LIFETIME` as the environment variable `KESTREL_DNS_CACHE_LIFETIME` and remove `dns_cache_lifetime`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
