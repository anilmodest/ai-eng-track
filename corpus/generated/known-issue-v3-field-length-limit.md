---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: field length limit after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.6 or later that changed the field length limit in version 2.

**What happens:** the version 2 setting `field_length_limit` is rejected by version 3. The service then runs on the version 3 default of 22 percent unless `KESTREL_FIELD_LENGTH_LIMIT` is set.

**Workaround:** set `KESTREL_FIELD_LENGTH_LIMIT` in the admin console and remove `field_length_limit`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
