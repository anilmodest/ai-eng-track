---
product: Kestrel Data Runner
version: v3
section: Known issues
---

# Known issue: tls handshake timeout after upgrading to version 3

**Affects:** installations upgraded from version 2 to version 3.6 or later that changed the tls handshake timeout in version 2.

**What happens:** the version 2 setting `tls_handshake_timeout_hou` is warned by version 3. The service then runs on the version 3 default of 25 hours unless `KESTREL_TLS_HANDSHAKE_TIMEOUT` is set.

**Workaround:** set `KESTREL_TLS_HANDSHAKE_TIMEOUT` as the environment variable `KESTREL_TLS_HANDSHAKE_TIMEOUT` and remove `tls_handshake_timeout_hou`.

**Status:** by design. The release notes for the release that changed it say so; the upgrade guide did not, and has been corrected.
