---
product: Kestrel Data Runner
section: FAQ
---

# Failed login lockout: frequently asked questions

Answers to the questions the support desk is asked most about this setting. Where the answer depends on the version, both are given.

**What is the default failed login lockout?**

In version 2 it is 57 connections; in version 3 it is 127 connections.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 419 in version 2 and 485 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `failed_login_lockout` to `KESTREL_FAILED_LOGIN_LOCKOUT` in release 3.2. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
