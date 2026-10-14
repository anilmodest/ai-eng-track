---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: maintenance window length after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.4 or later that changed the maintenance window length in version 2.

**What happens:** the version 2 setting `maintenance_window_length_con` is rejected by version 3. The service then runs on the version 3 default of 87 connections unless `KESTREL_MAINTENANCE_WINDOW_LENGTH` is set.

**Workaround:** set `KESTREL_MAINTENANCE_WINDOW_LENGTH` in the admin console and remove `maintenance_window_length_con`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
