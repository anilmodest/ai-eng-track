---
product: Kestrel Data Runner
section: Upgrading
---

# Upgrading from version 2 to version 3: data settings

Every setting below changed name, place or default between the versions. The last column says what version 3 does with the old setting if you leave it in place.

| Setting | Version 2 | Version 3 | Default v2 → v3 | Old setting in v3 |
| --- | --- | --- | --- | --- |
| Request timeout | `request_timeout` | `KESTREL_REQUEST_TIMEOUT` | 2 → 7 hours | ignored |
| Audit log retention | `audit_log_retention` | `KESTREL_AUDIT_LOG_RETENTION` | 22 → 129 connections | warned |
| Metrics flush interval | `metrics_flush_interval` | `KESTREL_METRICS_FLUSH_INTERVAL` | 52 → 2 hours | ignored |
| Source poll interval | `source_poll_interval` | `KESTREL_SOURCE_POLL_INTERVAL` | 44 → 29 minutes | ignored |
| Dead-letter retention | `dead_letter_retention` | `KESTREL_DEAD_LETTER_RETENTION` | 119 → 149 seconds | ignored |
