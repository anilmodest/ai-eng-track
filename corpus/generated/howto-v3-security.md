---
product: Kestrel Data Runner
version: v3
section: Security
---

# Security guide (Kestrel v3)

This guide covers every security setting in version 3 of Kestrel Data Runner. Read it before changing more than one setting at once: several interact.

| Setting | Name | Default | Range | Takes effect |
| --- | --- | --- | --- | --- |
| Session timeout | `KESTREL_SESSION_TIMEOUT` | 812 characters | 13–3905 | next job |
| Password minimum length | `KESTREL_PASSWORD_MINIMUM_LENGTH` | 674 requests per minute | 109–5840 | restart |
| Cache expiry | `KESTREL_CACHE_EXPIRY` | 1063 days | 59–3407 | next job |
| Search result limit | `KESTREL_SEARCH_RESULT_LIMIT` | 480 megabytes | 28–1693 | next job |
| Idle disconnect | `KESTREL_IDLE_DISCONNECT` | 2804 items | 164–9796 | immediately |
| Trace sampling rate | `KESTREL_TRACE_SAMPLING_RATE` | 30 minutes | 1–224 | restart |
| TLS handshake timeout | `KESTREL_TLS_HANDSHAKE_TIMEOUT` | 25 hours | 1–152 | restart |
| Batch commit size | `KESTREL_BATCH_COMMIT_SIZE` | 378 requests per minute | 53–5795 | immediately |

## Session timeout

This page describes the session timeout setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Password minimum length

This page describes the password minimum length setting in Kestrel Data Runner, a data runner that moves records between business systems. Most installations never change it; the ones that do usually change it after their first busy period, when the default turns out to be too tight or too loose.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## Cache expiry

Kestrel Data Runner is a data runner that moves records between business systems. The cache expiry setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Search result limit

Kestrel Data Runner is a data runner that moves records between business systems. The search result limit setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read at the start of each job. A job that is already running keeps the value it started with; the next job uses the new one. No restart is needed.

## Idle disconnect

Kestrel Data Runner is a data runner that moves records between business systems. The idle disconnect setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is reloaded within a few seconds of being changed. No restart is needed, and work already in progress picks up the new value on its next step.

## Trace sampling rate

Kestrel Data Runner is a data runner that moves records between business systems. The trace sampling rate setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read when the service starts. Changing it has no effect on a running service; restart it with `kestrelctl restart` for the new value to be used.

## TLS handshake timeout

Kestrel Data Runner is a data runner that moves records between business systems. The tls handshake timeout setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Batch commit size

Kestrel Data Runner is a data runner that moves records between business systems. The batch commit size setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

The value is reloaded within a few seconds of being changed. No restart is needed, and work already in progress picks up the new value on its next step.
