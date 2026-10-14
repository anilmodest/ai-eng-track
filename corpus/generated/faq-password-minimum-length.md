---
product: Kestrel Data Runner
section: FAQ
---

# Password minimum length: frequently asked questions

Answers to the questions the support desk is asked most about this setting. Where the answer depends on the version, both are given.

**What is the default password minimum length?**

In version 2 it is 1990 requests per minute; in version 3 it is 674 requests per minute.

**Do I need to restart after changing it?**

Version 2: no. Version 3: yes.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 5905 in version 2 and 5840 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `password_minimum_length_req` to `KESTREL_PASSWORD_MINIMUM_LENGTH` in release 3.3. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
