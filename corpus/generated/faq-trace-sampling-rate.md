---
product: Kestrel Data Runner
section: FAQ
---

# Trace sampling rate: frequently asked questions

The questions below come from real tickets, lightly edited. Check which version you run before you act on an answer.

**What is the default trace sampling rate?**

In version 2 it is 10 minutes; in version 3 it is 30 minutes.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: yes.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 219 in version 2 and 224 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `trace_sampling_rate_min` to `KESTREL_TRACE_SAMPLING_RATE` in release 3.1. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
