---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: webhook delivery timeout after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.4 or later that changed the webhook delivery timeout in version 2.

**What happens:** the version 2 setting `webhook_delivery_timeout_per` is warned by version 3. The service then runs on the version 3 default of 3 percent unless `KESTREL_WEBHOOK_DELIVERY_TIMEOUT` is set.

**Workaround:** set `KESTREL_WEBHOOK_DELIVERY_TIMEOUT` as the environment variable `KESTREL_WEBHOOK_DELIVERY_TIMEOUT` and remove `webhook_delivery_timeout_per`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
