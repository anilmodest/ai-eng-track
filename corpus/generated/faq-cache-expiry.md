---
product: Kestrel Data Runner
section: FAQ
---

# Cache expiry: frequently asked questions

The questions below come from real tickets, lightly edited. Check which version you run before you act on an answer.

**What is the default cache expiry?**

In version 2 it is 596 days; in version 3 it is 1063 days.

**Do I need to restart after changing it?**

Version 2: no. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 3364 in version 2 and 3407 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `cache_expiry` to `KESTREL_CACHE_EXPIRY` in release 3.7. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
