---
product: Kestrel Data Runner
section: Upgrading
---

# Upgrading from version 2 to version 3: configuration settings

Every setting below changed name, place or default between the versions. The last column says what version 3 does with the old setting if you leave it in place.

| Setting | Version 2 | Version 3 | Default v2 → v3 | Old setting in v3 |
| --- | --- | --- | --- | --- |
| Import file size limit | `import_file_size_limit_day` | `KESTREL_IMPORT_FILE_SIZE_LIMIT` | 66 → 74 days | warned |
| Backup schedule interval | `backup_schedule_interval` | `KESTREL_BACKUP_SCHEDULE_INTERVAL` | 66 → 45 minutes | rejected |
| Two-factor grace period | `two_factor_grace_period` | `KESTREL_TWO_FACTOR_GRACE_PERIOD` | 68 → 122 connections | warned |
| Health check interval | `health_check_interval` | `KESTREL_HEALTH_CHECK_INTERVAL` | 716 → 141 days | ignored |
| Archive threshold | `archive_threshold` | `KESTREL_ARCHIVE_THRESHOLD` | 32 → 21 minutes | warned |
| Concurrent session limit | `concurrent_session_limit_per` | `KESTREL_CONCURRENT_SESSION_LIMIT` | 26 → 16 percent | ignored |
| Field length limit | `field_length_limit` | `KESTREL_FIELD_LENGTH_LIMIT` | 3 → 22 percent | rejected |
