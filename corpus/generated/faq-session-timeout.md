---
product: Kestrel Data Runner
section: FAQ
---

# Session timeout: frequently asked questions

The questions below come from real tickets, lightly edited. Check which version you run before you act on an answer.

**What is the default session timeout?**

In version 2 it is 925 characters; in version 3 it is 812 characters.

**Do I need to restart after changing it?**

Version 2: no. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 3908 in version 2 and 3905 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `session_timeout_cha` to `KESTREL_SESSION_TIMEOUT` in release 3.8. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
