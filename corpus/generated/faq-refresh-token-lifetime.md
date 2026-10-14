---
product: Kestrel Data Runner
section: FAQ
---

# Refresh token lifetime: frequently asked questions

The questions below come from real tickets, lightly edited. Check which version you run before you act on an answer.

**What is the default refresh token lifetime?**

In version 2 it is 3 percent; in version 3 it is 15 percent.

**Do I need to restart after changing it?**

Version 2: no. Version 3: yes.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 83 in version 2 and 83 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `refresh_token_lifetime` to `KESTREL_REFRESH_TOKEN_LIFETIME` in release 3.4. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
