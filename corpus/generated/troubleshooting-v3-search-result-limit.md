---
product: Kestrel Data Runner
version: v3
section: Troubleshooting
---

# Troubleshooting: search result limit (Kestrel v3)

Start here when the search result limit does not behave as configured. Most reports turn out to be one of three causes, listed in the order to check them.

## Symptoms

- The service uses a different search result limit from the one you set.
- The log shows `E1693: KESTREL_SEARCH_RESULT_LIMIT out of range`.
- The value changed in configuration, but behaviour did not change.

## Check 1: is the value in range?

The accepted range is 28 to 1693 megabytes. Out of range, the value is rejected with `E1693: KESTREL_SEARCH_RESULT_LIMIT out of range` and the previous value stays in force. Run `kestrelctl config show KESTREL_SEARCH_RESULT_LIMIT` to see the value in use.

## Check 2: has it taken effect?

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Check 3: is the old setting still there?

Installations upgraded from version 2 often still carry `search_result_limit`. In version 3 it is warned. The setting that counts is `KESTREL_SEARCH_RESULT_LIMIT`, and its default is 480 megabytes.

## What the metrics show

The service exports the metric `kestrel_search_result_limit_limit_hits_total`. A steady rise means the limit is doing its job; a sudden jump after a change means the new value is too tight. Alert on the rate, not on the total.

## If none of these explains it

Collect the output of `kestrelctl config show --all` and the last hour of the service log, and open a ticket with the support desk. Say which version you run.
