---
product: Kestrel Data Runner
section: FAQ
---

# Dead-letter retention: frequently asked questions

Answers to the questions the support desk is asked most about this setting. Where the answer depends on the version, both are given.

**What is the default dead-letter retention?**

In version 2 it is 119 seconds; in version 3 it is 149 seconds.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 564 in version 2 and 580 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `dead_letter_retention` to `KESTREL_DEAD_LETTER_RETENTION` in release 3.5. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
