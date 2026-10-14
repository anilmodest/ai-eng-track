---
product: Kestrel Data Runner
section: FAQ
---

# Report page size: frequently asked questions

Answers to the questions the support desk is asked most about this setting. Where the answer depends on the version, both are given.

**What is the default report page size?**

In version 2 it is 65 connections; in version 3 it is 157 connections.

**Do I need to restart after changing it?**

Version 2: no. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 499 in version 2 and 499 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `report_page_size` to `KESTREL_REPORT_PAGE_SIZE` in release 3.2. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
