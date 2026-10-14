---
product: Kestrel Data Runner
section: FAQ
---

# Attachment size limit: frequently asked questions

The questions below come from real tickets, lightly edited. Check which version you run before you act on an answer.

**What is the default attachment size limit?**

In version 2 it is 508 days; in version 3 it is 499 days.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 3641 in version 2 and 3628 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `attachment_size_limit` to `KESTREL_ATTACHMENT_SIZE_LIMIT` in release 3.8. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
