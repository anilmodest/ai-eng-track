---
product: Kestrel Data Runner
section: FAQ
---

# Temporary file lifetime: frequently asked questions

The questions below come from real tickets, lightly edited. Check which version you run before you act on an answer.

**What is the default temporary file lifetime?**

In version 2 it is 134 seconds; in version 3 it is 162 seconds.

**Do I need to restart after changing it?**

Version 2: no. Version 3: yes.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 533 in version 2 and 566 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `temporary_file_lifetime_sec` to `KESTREL_TEMPORARY_FILE_LIFETIME` in release 3.6. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
