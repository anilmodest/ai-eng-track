---
product: Kestrel Data Runner
section: FAQ
---

# DNS cache lifetime: frequently asked questions

Answers to the questions the support desk is asked most about this setting. Where the answer depends on the version, both are given.

**What is the default dns cache lifetime?**

In version 2 it is 2822 items; in version 3 it is 1959 items.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 8583 in version 2 and 9472 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `dns_cache_lifetime` to `KESTREL_DNS_CACHE_LIFETIME` in release 3.3. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
