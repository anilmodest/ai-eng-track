---
product: Kestrel Data Runner
section: FAQ
---

# Pagination cursor lifetime: frequently asked questions

The questions below come from real tickets, lightly edited. Check which version you run before you act on an answer.

**What is the default pagination cursor lifetime?**

In version 2 it is 33 percent; in version 3 it is 23 percent.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: yes.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 99 in version 2 and 87 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `pagination_cursor_lifetime` to `KESTREL_PAGINATION_CURSOR_LIFETIME` in release 3.1. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
