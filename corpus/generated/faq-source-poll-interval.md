---
product: Kestrel Data Runner
section: FAQ
---

# Source poll interval: frequently asked questions

The questions below come from real tickets, lightly edited. Check which version you run before you act on an answer.

**What is the default source poll interval?**

In version 2 it is 44 minutes; in version 3 it is 29 minutes.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 210 in version 2 and 193 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `source_poll_interval` to `KESTREL_SOURCE_POLL_INTERVAL` in release 3.2. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
