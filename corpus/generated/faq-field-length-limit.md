---
product: Kestrel Data Runner
section: FAQ
---

# Field length limit: frequently asked questions

Answers to the questions the support desk is asked most about this setting. Where the answer depends on the version, both are given.

**What is the default field length limit?**

In version 2 it is 3 percent; in version 3 it is 22 percent.

**Do I need to restart after changing it?**

Version 2: no. Version 3: yes.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 100 in version 2 and 79 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `field_length_limit` to `KESTREL_FIELD_LENGTH_LIMIT` in release 3.6. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
