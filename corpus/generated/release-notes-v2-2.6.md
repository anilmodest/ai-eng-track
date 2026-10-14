---
product: Kestrel Data Runner
version: v2
section: Release notes
---

# Kestrel 2.6 release notes

Released 8 July 2024.

## Changes

- Attachment size limit: the error `E1894: attachment_size_limit out of range` now names the accepted range (23 to 3641 days).
- Scheduler worker count: the error `E1929: scheduler_worker_count out of range` now names the accepted range (1 to 209 minutes).
- Transform memory limit: the error `E1915: transform_memory_limit out of range` now names the accepted range (6 to 394 connections).

## Fixes

- Fixed a case where health check interval was not applied to the first job after a restart.
- Fixed a case where export batch size was not applied to the first job after a backup restore.
- Fixed a case where batch commit size was not applied to the first job after a backup restore.
- Fixed a case where upload chunk size was not applied to the first job after a restart.
- Fixed a case where webhook retry count was not applied to the first job after a failover.
