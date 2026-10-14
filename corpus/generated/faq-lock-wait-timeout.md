---
product: Kestrel Data Runner
section: FAQ
---

# Lock wait timeout: frequently asked questions

The questions below come from real tickets, lightly edited. Check which version you run before you act on an answer.

**What is the default lock wait timeout?**

In version 2 it is 3 percent; in version 3 it is 27 percent.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 81 in version 2 and 88 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `lock_wait_timeout_per` to `KESTREL_LOCK_WAIT_TIMEOUT` in release 3.6. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
