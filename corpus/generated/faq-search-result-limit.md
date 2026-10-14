---
product: Kestrel Data Runner
section: FAQ
---

# Search result limit: frequently asked questions

Answers to the questions the support desk is asked most about this setting. Where the answer depends on the version, both are given.

**What is the default search result limit?**

In version 2 it is 394 megabytes; in version 3 it is 480 megabytes.

**Do I need to restart after changing it?**

Version 2: no. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 1745 in version 2 and 1693 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `search_result_limit` to `KESTREL_SEARCH_RESULT_LIMIT` in release 3.8. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
