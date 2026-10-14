---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: upload chunk size after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.7 or later that changed the upload chunk size in version 2.

**What happens:** the version 2 setting `upload_chunk_size` is rejected by version 3. The service then runs on the version 3 default of 97 seconds unless `KESTREL_UPLOAD_CHUNK_SIZE` is set.

**Workaround:** set `KESTREL_UPLOAD_CHUNK_SIZE` in the admin console and remove `upload_chunk_size`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
