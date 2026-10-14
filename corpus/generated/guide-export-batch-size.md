---
product: Kestrel Data Runner
section: Operations
---

# Operating the export batch size

In Kestrel Data Runner, the export batch size is a single value measured in seconds. It applies to the whole installation rather than to one customer account, which is why it lives in system configuration and not in account settings.

## How it works

Every request carries the export batch size that applied when it started. If the value changes while a request is in progress, that request keeps its original limit, and only new requests see the new one. This keeps behaviour predictable during a change, at the cost of a short period in which old and new limits are both in force.

## Choosing a value

Start from the default of 57 seconds and change it only with a reason you can write down. Raising the export batch size trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 571 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_export_batch_size_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Version differences in one table

| | Version 2 | Version 3 |
| --- | --- | --- |
| Setting | `export_batch_size_sec` | `KESTREL_EXPORT_BATCH_SIZE` |
| Default | 146 seconds | 57 seconds |
| Range | 6–470 | 7–571 |
| Takes effect | restart | next job |

## A worked change

An administrator lowered the export batch size to the minimum while testing and forgot to restore it. Failures tripled overnight. The activity log named the setting on every failure, which is how support found it in minutes rather than days.
