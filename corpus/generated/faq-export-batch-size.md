---
product: Kestrel Data Runner
section: FAQ
---

# Export batch size: frequently asked questions

Answers to the questions the support desk is asked most about this setting. Where the answer depends on the version, both are given.

**What is the default export batch size?**

In version 2 it is 146 seconds; in version 3 it is 57 seconds.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 470 in version 2 and 571 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `export_batch_size_sec` to `KESTREL_EXPORT_BATCH_SIZE` in release 3.1. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
