---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: temporary file lifetime after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.6 or later that changed the temporary file lifetime in version 2.

**What happens:** the version 2 setting `temporary_file_lifetime_sec` is ignored by version 3. The service then runs on the version 3 default of 162 seconds unless `KESTREL_TEMPORARY_FILE_LIFETIME` is set.

**Workaround:** set `KESTREL_TEMPORARY_FILE_LIFETIME` as the environment variable `KESTREL_TEMPORARY_FILE_LIFETIME` and remove `temporary_file_lifetime_sec`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
