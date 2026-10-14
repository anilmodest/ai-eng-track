---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: import file size limit after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.2 or later that changed the import file size limit in version 2.

**What happens:** the version 2 setting `import_file_size_limit_day` is warned by version 3. The service then runs on the version 3 default of 74 days unless `KESTREL_IMPORT_FILE_SIZE_LIMIT` is set.

**Workaround:** set `KESTREL_IMPORT_FILE_SIZE_LIMIT` as the environment variable `KESTREL_IMPORT_FILE_SIZE_LIMIT` and remove `import_file_size_limit_day`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
