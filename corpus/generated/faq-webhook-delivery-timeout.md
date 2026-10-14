---
product: Kestrel Data Runner
section: FAQ
---

# Webhook delivery timeout: frequently asked questions

Answers to the questions the support desk is asked most about this setting. Where the answer depends on the version, both are given.

**What is the default webhook delivery timeout?**

In version 2 it is 25 percent; in version 3 it is 3 percent.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 93 in version 2 and 94 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `webhook_delivery_timeout_per` to `KESTREL_WEBHOOK_DELIVERY_TIMEOUT` in release 3.4. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
