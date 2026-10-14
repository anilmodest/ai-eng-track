---
product: Kestrel Data Runner
version: v2
section: Operations
---

# Operations guide (Kestrel v2)

This guide covers every operations setting in version 2 of Kestrel Data Runner. Read it before changing more than one setting at once: several interact.

| Setting | Name | Default | Range | Takes effect |
| --- | --- | --- | --- | --- |
| Export batch size | `export_batch_size_sec` | 146 seconds | 6–470 | restart |
| API rate limit | `api_rate_limit` | 161 items | 98–7564 | next job |
| Webhook delivery timeout | `webhook_delivery_timeout_per` | 25 percent | 1–93 | restart |
| Webhook retry count | `webhook_retry_count` | 12 percent | 1–97 | restart |
| Failed login lockout | `failed_login_lockout` | 57 connections | 3–419 | restart |
| Job queue depth | `job_queue_depth` | 4 minutes | 1–213 | restart |
| Token lifetime | `token_lifetime` | 788 days | 39–3464 | restart |
| Refresh token lifetime | `refresh_token_lifetime` | 3 percent | 2–83 | next job |
| Bulk update limit | `bulk_update_limit` | 42 hours | 4–164 | restart |
| Attachment size limit | `attachment_size_limit` | 508 days | 23–3641 | restart |
| Sync interval | `sync_interval` | 619 megabytes | 30–1861 | next job |
| Pagination cursor lifetime | `pagination_cursor_lifetime` | 33 percent | 1–99 | restart |
| Maintenance window length | `maintenance_window_length_con` | 104 connections | 6–393 | next job |
| Temporary file lifetime | `temporary_file_lifetime_sec` | 134 seconds | 7–533 | next job |
| Transform memory limit | `transform_memory_limit` | 7 connections | 6–394 | next job |

## Export batch size

This page describes the export batch size setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## API rate limit

In Kestrel Data Runner, the api rate limit is a single value measured in items. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Webhook delivery timeout

This page describes the webhook delivery timeout setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Webhook retry count

This page describes the webhook retry count setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Failed login lockout

This page describes the failed login lockout setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Job queue depth

This page describes the job queue depth setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Token lifetime

Kestrel Data Runner is a data runner that moves records between business systems. The token lifetime setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Refresh token lifetime

This page describes the refresh token lifetime setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Bulk update limit

Kestrel Data Runner is a data runner that moves records between business systems. The bulk update limit setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Attachment size limit

This page describes the attachment size limit setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Sync interval

This page describes the sync interval setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Pagination cursor lifetime

Kestrel Data Runner is a data runner that moves records between business systems. The pagination cursor lifetime setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Maintenance window length

This page describes the maintenance window length setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Temporary file lifetime

This page describes the temporary file lifetime setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Transform memory limit

Kestrel Data Runner is a data runner that moves records between business systems. The transform memory limit setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

A change applies from the next job onwards. Jobs already running finish with the value they started with.
