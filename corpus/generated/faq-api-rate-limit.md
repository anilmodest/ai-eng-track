---
product: Kestrel Data Runner
section: FAQ
---

# API rate limit: frequently asked questions

The questions below come from real tickets, lightly edited. Check which version you run before you act on an answer.

**What is the default api rate limit?**

In version 2 it is 161 items; in version 3 it is 1542 items.

**Do I need to restart after changing it?**

Version 2: no. Version 3: yes.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 7564 in version 2 and 7962 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `api_rate_limit` to `KESTREL_API_RATE_LIMIT` in release 3.1. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
