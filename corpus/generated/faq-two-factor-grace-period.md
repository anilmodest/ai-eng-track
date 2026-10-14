---
product: Kestrel Data Runner
section: FAQ
---

# Two-factor grace period: frequently asked questions

Answers to the questions the support desk is asked most about this setting. Where the answer depends on the version, both are given.

**What is the default two-factor grace period?**

In version 2 it is 68 connections; in version 3 it is 122 connections.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: yes.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 404 in version 2 and 466 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `two_factor_grace_period` to `KESTREL_TWO_FACTOR_GRACE_PERIOD` in release 3.6. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
