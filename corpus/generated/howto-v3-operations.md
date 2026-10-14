---
product: Kestrel Data Runner
version: v3
section: Operations
---

# Operations guide (Kestrel v3)

This guide covers every operations setting in version 3 of Kestrel Data Runner. Read it before changing more than one setting at once: several interact.

| Setting | Name | Default | Range | Takes effect |
| --- | --- | --- | --- | --- |
| Export batch size | `KESTREL_EXPORT_BATCH_SIZE` | 57 seconds | 7–571 | next job |
| API rate limit | `KESTREL_API_RATE_LIMIT` | 1542 items | 152–7962 | restart |
| Webhook delivery timeout | `KESTREL_WEBHOOK_DELIVERY_TIMEOUT` | 3 percent | 2–94 | next job |
| Webhook retry count | `KESTREL_WEBHOOK_RETRY_COUNT` | 18 percent | 2–86 | restart |
| Failed login lockout | `KESTREL_FAILED_LOGIN_LOCKOUT` | 127 connections | 6–485 | immediately |
| Job queue depth | `KESTREL_JOB_QUEUE_DEPTH` | 79 minutes | 2–239 | immediately |
| Token lifetime | `KESTREL_TOKEN_LIFETIME` | 836 days | 52–2768 | restart |
| Refresh token lifetime | `KESTREL_REFRESH_TOKEN_LIFETIME` | 15 percent | 2–83 | restart |
| Bulk update limit | `KESTREL_BULK_UPDATE_LIMIT` | 9 hours | 4–128 | next job |
| Attachment size limit | `KESTREL_ATTACHMENT_SIZE_LIMIT` | 499 days | 46–3628 | next job |
| Sync interval | `KESTREL_SYNC_INTERVAL` | 383 megabytes | 31–1577 | next job |
| Pagination cursor lifetime | `KESTREL_PAGINATION_CURSOR_LIFETIME` | 23 percent | 1–87 | restart |
| Maintenance window length | `KESTREL_MAINTENANCE_WINDOW_LENGTH` | 87 connections | 1–482 | restart |
| Temporary file lifetime | `KESTREL_TEMPORARY_FILE_LIFETIME` | 162 seconds | 8–566 | restart |
| Transform memory limit | `KESTREL_TRANSFORM_MEMORY_LIMIT` | 19 connections | 10–400 | next job |

## Export batch size

Kestrel Data Runner is a data runner that moves records between business systems. The export batch size setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## API rate limit

Kestrel Data Runner is a data runner that moves records between business systems. The api rate limit setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Webhook delivery timeout

Kestrel Data Runner is a data runner that moves records between business systems. The webhook delivery timeout setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Webhook retry count

This page describes the webhook retry count setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Failed login lockout

In Kestrel Data Runner, the failed login lockout is a single value measured in connections. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Job queue depth

Kestrel Data Runner is a data runner that moves records between business systems. The job queue depth setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Token lifetime

Kestrel Data Runner is a data runner that moves records between business systems. The token lifetime setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Refresh token lifetime

Kestrel Data Runner is a data runner that moves records between business systems. The refresh token lifetime setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Bulk update limit

In Kestrel Data Runner, the bulk update limit is a single value measured in hours. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Attachment size limit

In Kestrel Data Runner, the attachment size limit is a single value measured in days. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Sync interval

In Kestrel Data Runner, the sync interval is a single value measured in megabytes. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Pagination cursor lifetime

In Kestrel Data Runner, the pagination cursor lifetime is a single value measured in percent. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Maintenance window length

In Kestrel Data Runner, the maintenance window length is a single value measured in connections. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Temporary file lifetime

In Kestrel Data Runner, the temporary file lifetime is a single value measured in seconds. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Transform memory limit

Kestrel Data Runner is a data runner that moves records between business systems. The transform memory limit setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

A change applies from the next job onwards. Jobs already running finish with the value they started with.
