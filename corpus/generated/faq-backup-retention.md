---
product: Kestrel Data Runner
section: FAQ
---

# Backup retention: frequently asked questions

The questions below come from real tickets, lightly edited. Check which version you run before you act on an answer.

**What is the default backup retention?**

In version 2 it is 496 requests per minute; in version 3 it is 518 requests per minute.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: yes.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 5504 in version 2 and 5059 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `backup_retention` to `KESTREL_BACKUP_RETENTION` in release 3.9. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
