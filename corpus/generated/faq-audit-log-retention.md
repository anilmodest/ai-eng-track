---
product: Kestrel Data Runner
section: FAQ
---

# Audit log retention: frequently asked questions

The questions below come from real tickets, lightly edited. Check which version you run before you act on an answer.

**What is the default audit log retention?**

In version 2 it is 22 connections; in version 3 it is 129 connections.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: yes.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 406 in version 2 and 458 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `audit_log_retention` to `KESTREL_AUDIT_LOG_RETENTION` in release 3.4. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
