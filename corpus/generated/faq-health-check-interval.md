---
product: Kestrel Data Runner
section: FAQ
---

# Health check interval: frequently asked questions

Answers to the questions the support desk is asked most about this setting. Where the answer depends on the version, both are given.

**What is the default health check interval?**

In version 2 it is 716 days; in version 3 it is 141 days.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 3245 in version 2 and 2915 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `health_check_interval` to `KESTREL_HEALTH_CHECK_INTERVAL` in release 3.0. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
