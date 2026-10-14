---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: report page size after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.2 or later that changed the report page size in version 2.

**What happens:** the version 2 setting `report_page_size` is rejected by version 3. The service then runs on the version 3 default of 157 connections unless `KESTREL_REPORT_PAGE_SIZE` is set.

**Workaround:** set `KESTREL_REPORT_PAGE_SIZE` as the environment variable `KESTREL_REPORT_PAGE_SIZE` and remove `report_page_size`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
