---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: dns cache lifetime (Kestrel v3)

Problems with the dns cache lifetime are almost always configuration, not defects. Work through the checks below before opening a ticket.

## Symptoms

- The service uses a different dns cache lifetime from the one you set.
- The log shows `E1978: KESTREL_DNS_CACHE_LIFETIME out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 79 to 9472 items. Out of range, the value is rejected with `E1978: KESTREL_DNS_CACHE_LIFETIME out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_DNS_CACHE_LIFETIME` to see the value in use.

## Check 2: has it taken effect?

Changes take effect immediately: the service watches the setting and reloads it without a restart.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `dns_cache_lifetime`. In version 3 it is warned. The setting that counts is `KESTREL_DNS_CACHE_LIFETIME`, and its default is 1959 items.

## What the metrics show

Watch `kestrel_dns_cache_lifetime_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
