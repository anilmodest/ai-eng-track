---
product: Kestrel Data Runner
section: FAQ
---

# Backup schedule interval: frequently asked questions

The questions below come from real tickets, lightly edited. Check which version you run before you act on an answer.

**What is the default backup schedule interval?**

In version 2 it is 66 minutes; in version 3 it is 45 minutes.

**Do I need to restart after changing it?**

Version 2: no. Version 3: yes.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 229 in version 2 and 194 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `backup_schedule_interval` to `KESTREL_BACKUP_SCHEDULE_INTERVAL` in release 3.1. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
