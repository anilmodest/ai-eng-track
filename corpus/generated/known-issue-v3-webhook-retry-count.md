---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: webhook retry count after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.6 or later that changed the webhook retry count in version 2.

**What happens:** the version 2 setting `webhook_retry_count` is warned by version 3. The service then runs on the version 3 default of 18 percent unless `KESTREL_WEBHOOK_RETRY_COUNT` is set.

**Workaround:** set `KESTREL_WEBHOOK_RETRY_COUNT` in the admin console and remove `webhook_retry_count`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
