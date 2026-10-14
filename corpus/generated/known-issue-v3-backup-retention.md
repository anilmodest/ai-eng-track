---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: backup retention after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.9 or later that changed the backup retention in version 2.

**What happens:** the version 2 setting `backup_retention` is warned by version 3. The service then runs on the version 3 default of 518 requests per minute unless `KESTREL_BACKUP_RETENTION` is set.

**Workaround:** set `KESTREL_BACKUP_RETENTION` as the environment variable `KESTREL_BACKUP_RETENTION` and remove `backup_retention`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
