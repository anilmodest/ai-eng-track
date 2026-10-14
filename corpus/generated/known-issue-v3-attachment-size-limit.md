---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: attachment size limit after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.8 or later that changed the attachment size limit in version 2.

**What happens:** the version 2 setting `attachment_size_limit` is rejected by version 3. The service then runs on the version 3 default of 499 days unless `KESTREL_ATTACHMENT_SIZE_LIMIT` is set.

**Workaround:** set `KESTREL_ATTACHMENT_SIZE_LIMIT` as the environment variable `KESTREL_ATTACHMENT_SIZE_LIMIT` and remove `attachment_size_limit`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
