---
product: Kestrel Data Runner
section: FAQ
---

# Connection pool size: frequently asked questions

The questions below come from real tickets, lightly edited. Check which version you run before you act on an answer.

**What is the default connection pool size?**

In version 2 it is 55 minutes; in version 3 it is 33 minutes.

**Do I need to restart after changing it?**

Version 2: no. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 193 in version 2 and 230 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `connection_pool_size_min` to `KESTREL_CONNECTION_POOL_SIZE` in release 3.5. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
