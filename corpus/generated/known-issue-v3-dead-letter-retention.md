---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: dead-letter retention after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.5 or later that changed the dead-letter retention in version 2.

**What happens:** the version 2 setting `dead_letter_retention` is ignored by version 3. The service then runs on the version 3 default of 149 seconds unless `KESTREL_DEAD_LETTER_RETENTION` is set.

**Workaround:** set `KESTREL_DEAD_LETTER_RETENTION` as the environment variable `KESTREL_DEAD_LETTER_RETENTION` and remove `dead_letter_retention`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
