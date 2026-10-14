---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: backup schedule interval after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.1 or later that changed the backup schedule interval in version 2.

**What happens:** the version 2 setting `backup_schedule_interval` is rejected by version 3. The service then runs on the version 3 default of 45 minutes unless `KESTREL_BACKUP_SCHEDULE_INTERVAL` is set.

**Workaround:** set `KESTREL_BACKUP_SCHEDULE_INTERVAL` as the environment variable `KESTREL_BACKUP_SCHEDULE_INTERVAL` and remove `backup_schedule_interval`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
