---
product: Kestrel Data Runner
version: v2
section: Security
---

# Security guide (Kestrel v2)

This guide covers every security setting in version 2 of Kestrel Data Runner. Read it before changing more than one setting at once: several interact.

| Setting | Name | Default | Range | Takes effect |
| --- | --- | --- | --- | --- |
| Session timeout | `session_timeout_cha` | 925 characters | 60–3908 | next job |
| Password minimum length | `password_minimum_length_req` | 1990 requests per minute | 96–5905 | next job |
| Cache expiry | `cache_expiry` | 596 days | 55–3364 | next job |
| Search result limit | `search_result_limit` | 394 megabytes | 28–1745 | next job |
| Idle disconnect | `idle_disconnect` | 1917 items | 66–9959 | restart |
| Trace sampling rate | `trace_sampling_rate_min` | 10 minutes | 5–219 | restart |
| TLS handshake timeout | `tls_handshake_timeout_hou` | 47 hours | 1–146 | restart |
| Batch commit size | `batch_commit_size` | 1045 requests per minute | 31–5436 | restart |

## Session timeout

Kestrel Data Runner is a data runner that moves records between business systems. The session timeout setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Password minimum length

This page describes the password minimum length setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Cache expiry

This page describes the cache expiry setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Search result limit

In Kestrel Data Runner, the search result limit is a single value measured in megabytes. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Idle disconnect

In Kestrel Data Runner, the idle disconnect is a single value measured in items. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Trace sampling rate

In Kestrel Data Runner, the trace sampling rate is a single value measured in minutes. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## TLS handshake timeout

This page describes the tls handshake timeout setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Batch commit size

Kestrel Data Runner is a data runner that moves records between business systems. The batch commit size setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.
