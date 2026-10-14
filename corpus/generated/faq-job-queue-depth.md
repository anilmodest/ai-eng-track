---
product: Kestrel Data Runner
section: FAQ
---

# Job queue depth: frequently asked questions

Answers to the questions the support desk is asked most about this setting. Where the answer depends on the version, both are given.

**What is the default job queue depth?**

In version 2 it is 4 minutes; in version 3 it is 79 minutes.

**Do I need to restart after changing it?**

Version 2: yes. Version 3: no.

**What happens if I set it too high?**

The value is rejected and the previous one stays in force. The maximum is 213 in version 2 and 239 in version 3.

**We upgraded and the setting seems to have reset. Why?**

Version 3 changed the setting's name from `job_queue_depth` to `KESTREL_JOB_QUEUE_DEPTH` in release 3.3. See the known issue for this setting.

**Can it be set per customer account?**

No. It applies to the whole installation.
