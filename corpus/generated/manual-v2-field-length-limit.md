---
product: Kestrel Data Runner
version: v2
section: Configuration
---

# Field length limit (Kestrel v2)

Kestrel Data Runner is a data runner that moves records between business systems. The field length limit setting controls how the service behaves when that limit is reached, and it is one of the settings most often changed by administrators after go-live.

## Where the setting lives

The setting is `field_length_limit`, in `kestrel.conf`, in the `[storage]` block. It takes a whole number of percent. The default is **3 percent**.

```
field_length_limit = 3
```

## How it works

Internally, the service checks the field length limit every time the limit could apply, not on a timer. When the limit is reached the service finishes the step it is on, records an event in the activity log, and only then applies the limit. A value of 3 percent therefore means 'at least 3', never 'exactly', and on a heavily loaded installation the difference can be noticeable. The activity log entry names the setting, so an administrator can always tell which limit was hit.

## When it takes effect

A change applies from the next job onwards. Jobs already running finish with the value they started with.

## Choosing a value

Start from the default of 3 percent and change it only with a reason you can write down. Raising the field length limit trades resilience for capacity: more work is accepted, but a failure takes longer to notice. Lowering it does the opposite. Change it in steps of no more than a quarter, watch for a week, and record what you saw. Installations that jumped straight to the maximum of 100 are the most common source of tickets about this setting.

## Monitoring

Watch `kestrel_field_length_limit_current` on the operations dashboard. If it sits at the configured value for long periods, the setting is the bottleneck, and raising it is reasonable. If it never comes near, the value can safely stay where it is.

## Limits

The lowest accepted value is 2. The highest accepted value is 100. A value outside that range is rejected and the previous value stays in force, with `E1807: field_length_limit out of range` in the log.

## Examples

| Value (percent) | When to use it |
| --- | --- |
| 2 | small installations, or testing |
| 3 | the default; right for most installations |
| 6 | busy installations with spare capacity |
| 100 | the maximum; only with a reason written down |

## Interactions

The field length limit is often changed together with the import file size limit (`import_file_size_limit_day`, default 66 days in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

The field length limit is often changed together with the backup schedule interval (`backup_schedule_interval`, default 66 minutes in version 2). Change one at a time: when both move at once, it is impossible to tell from the metrics which change helped and which hurt.

## Version history

Introduced in version 2.0 as `field_length_limit`. Unchanged through the 2.x releases apart from clearer error messages.

## Related

- Import file size limit: see the Import file size limit page for version 2.
- Backup schedule interval: see the Backup schedule interval page for version 2.
