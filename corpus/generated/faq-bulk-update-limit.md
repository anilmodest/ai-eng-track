---
product: Kestrel Data Runner
section: FAQ
---

# Bulk update limit: frequently asked questions

The questions below come from real tickets, lightly edited. Check which version you run before you act on an answer.

**What is the default bulk update limit?**

In version 2 it is 42 hours; in version 3 it is 9 hours.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 164 in version 2 and 128 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `bulk_update_limit` to `KESTREL_BULK_UPDATE_LIMIT` in release 3.6. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
