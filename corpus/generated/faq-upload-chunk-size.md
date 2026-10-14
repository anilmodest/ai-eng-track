---
product: Kestrel Data Runner
section: FAQ
---

# Upload chunk size: frequently asked questions

The questions below come from real tickets, lightly edited. Check which version you run before you act on an answer.

**What is the default upload chunk size?**

In version 2 it is 104 seconds; in version 3 it is 97 seconds.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 586 in version 2 and 507 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `upload_chunk_size` to `KESTREL_UPLOAD_CHUNK_SIZE` in release 3.7. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
