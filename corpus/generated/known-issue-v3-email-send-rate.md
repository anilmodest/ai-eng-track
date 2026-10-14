---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: email send rate after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.2 or later that changed the email send rate in version 2.

**What happens:** the version 2 setting `email_send_rate` is warned by version 3. The service then runs on the version 3 default of 2131 items unless `KESTREL_EMAIL_SEND_RATE` is set.

**Workaround:** set `KESTREL_EMAIL_SEND_RATE` in the admin console and remove `email_send_rate`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
