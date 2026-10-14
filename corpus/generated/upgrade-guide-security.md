---
product: Kestrel Data Runner
section: Upgrading
---

# Upgrading from version 2 to version 3: security settings

Every setting below changed name, place or default between the versions. The last column says what version 3 does with the old setting if you leave it in place.

| Setting | Version 2 | Version 3 | Default v2 → v3 | Old setting in v3 |
| --- | --- | --- | --- | --- |
| Session timeout | `session_timeout_cha` | `KESTREL_SESSION_TIMEOUT` | 925 → 812 characters | rejected |
| Password minimum length | `password_minimum_length_req` | `KESTREL_PASSWORD_MINIMUM_LENGTH` | 1990 → 674 requests per minute | warned |
| Cache expiry | `cache_expiry` | `KESTREL_CACHE_EXPIRY` | 596 → 1063 days | rejected |
| Search result limit | `search_result_limit` | `KESTREL_SEARCH_RESULT_LIMIT` | 394 → 480 megabytes | warned |
| Idle disconnect | `idle_disconnect` | `KESTREL_IDLE_DISCONNECT` | 1917 → 2804 items | warned |
| Trace sampling rate | `trace_sampling_rate_min` | `KESTREL_TRACE_SAMPLING_RATE` | 10 → 30 minutes | ignored |
| TLS handshake timeout | `tls_handshake_timeout_hou` | `KESTREL_TLS_HANDSHAKE_TIMEOUT` | 47 → 25 hours | warned |
| Batch commit size | `batch_commit_size` | `KESTREL_BATCH_COMMIT_SIZE` | 1045 → 378 requests per minute | warned |
