---
product: Kestrel Data Runner
section: FAQ
---

# Idle disconnect: frequently asked questions

The questions below come from real tickets, lightly edited. Check which version you run before you act on an answer.

**What is the default idle disconnect?**

In version 2 it is 1917 items; in version 3 it is 2804 items.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 9959 in version 2 and 9796 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `idle_disconnect` to `KESTREL_IDLE_DISCONNECT` in release 3.4. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
