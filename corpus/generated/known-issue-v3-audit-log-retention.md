---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: audit log retention after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.4 or later that changed the audit log retention in version 2.

**What happens:** the version 2 setting `audit_log_retention` is warned by version 3. The service then runs on the version 3 default of 129 connections unless `KESTREL_AUDIT_LOG_RETENTION` is set.

**Workaround:** set `KESTREL_AUDIT_LOG_RETENTION` as the environment variable `KESTREL_AUDIT_LOG_RETENTION` and remove `audit_log_retention`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
