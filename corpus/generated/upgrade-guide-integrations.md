---
product: Kestrel Data Runner
section: Upgrading
---

# Upgrading from version 2 to version 3: integrations settings

Every setting below changed name, place or default between the versions. The last column says what version 3 does with the old setting if you leave it in place.

| Setting | Version 2 | Version 3 | Default v2 → v3 | Old setting in v3 |
| --- | --- | --- | --- | --- |
| Connection pool size | `connection_pool_size_min` | `KESTREL_CONNECTION_POOL_SIZE` | 55 → 33 minutes | warned |
| Backup retention | `backup_retention` | `KESTREL_BACKUP_RETENTION` | 496 → 518 requests per minute | warned |
| Password expiry | `password_expiry` | `KESTREL_PASSWORD_EXPIRY` | 114 → 38 connections | ignored |
| Notification digest interval | `notification_digest_interval` | `KESTREL_NOTIFICATION_DIGEST_INTERVAL` | 297 → 597 characters | ignored |
| Email send rate | `email_send_rate` | `KESTREL_EMAIL_SEND_RATE` | 2404 → 2131 items | warned |
| Report page size | `report_page_size` | `KESTREL_REPORT_PAGE_SIZE` | 65 → 157 connections | rejected |
| Scheduler worker count | `scheduler_worker_count` | `KESTREL_SCHEDULER_WORKER_COUNT` | 18 → 28 minutes | rejected |
| Upload chunk size | `upload_chunk_size` | `KESTREL_UPLOAD_CHUNK_SIZE` | 104 → 97 seconds | rejected |
| Purge delay | `purge_delay_ite` | `KESTREL_PURGE_DELAY` | 2028 → 2444 items | rejected |
| DNS cache lifetime | `dns_cache_lifetime` | `KESTREL_DNS_CACHE_LIFETIME` | 2822 → 1959 items | warned |
| Lock wait timeout | `lock_wait_timeout_per` | `KESTREL_LOCK_WAIT_TIMEOUT` | 3 → 27 percent | warned |
