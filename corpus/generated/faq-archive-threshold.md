---
product: Kestrel Data Runner
section: FAQ
---

# Archive threshold: frequently asked questions

The questions below come from real tickets, lightly edited. Check which version you run before you act on an answer.

**What is the default archive threshold?**

In version 2 it is 32 minutes; in version 3 it is 21 minutes.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 234 in version 2 and 235 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `archive_threshold` to `KESTREL_ARCHIVE_THRESHOLD` in release 3.6. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
