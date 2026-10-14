---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: notification digest interval after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.2 or later that changed the notification digest interval in version 2.

**What happens:** the version 2 setting `notification_digest_interval` is ignored by version 3. The service then runs on the version 3 default of 597 characters unless `KESTREL_NOTIFICATION_DIGEST_INTERVAL` is set.

**Workaround:** set `KESTREL_NOTIFICATION_DIGEST_INTERVAL` as the environment variable `KESTREL_NOTIFICATION_DIGEST_INTERVAL` and remove `notification_digest_interval`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
