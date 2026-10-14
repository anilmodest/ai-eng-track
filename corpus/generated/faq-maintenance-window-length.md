---
product: Kestrel Data Runner
section: FAQ
---

# Maintenance window length: frequently asked questions

Answers to the questions the support desk is asked most about this setting. Where the answer depends on the version, both are given.

**What is the default maintenance window length?**

In version 2 it is 104 connections; in version 3 it is 87 connections.

**Do I need to restart after changing it?**

Version 2: no. Version 3: yes.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 393 in version 2 and 482 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `maintenance_window_length_con` to `KESTREL_MAINTENANCE_WINDOW_LENGTH` in release 3.4. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
