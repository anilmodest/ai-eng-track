---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: backup retention (Kestrel v3)

Start here when the backup retention does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different backup retention from the one you set.
- The log shows `E1956: KESTREL_BACKUP_RETENTION out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 110 to 5059 requests per minute. Out of range, the value is rejected with `E1956: KESTREL_BACKUP_RETENTION out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_BACKUP_RETENTION` to see the value in use.

## Check 2: has it taken effect?

The value is read once, at startup. A running service keeps the old value until it is restarted with `kestrelctl restart`.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `backup_retention`. In version 3 it is warned. The setting that counts is `KESTREL_BACKUP_RETENTION`, and its default is 518 requests per minute.

## What the metrics show

Watch `kestrel_backup_retention_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
