---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: audit log retention (Kestrel v3)

Problems with the audit log retention are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different audit log retention from the one you set.
- The log shows `E1710: KESTREL_AUDIT_LOG_RETENTION out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 2 to 458 connections. Out of range, the value is rejected with `E1710: KESTREL_AUDIT_LOG_RETENTION out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_AUDIT_LOG_RETENTION` to see the value in use.

## Check 2: has it taken effect?

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `audit_log_retention`. In version 3 it is warned. The setting that counts is `KESTREL_AUDIT_LOG_RETENTION`, and its default is 129 connections.

## What the metrics show

The service exports the metric `kestrel_audit_log_retention_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
