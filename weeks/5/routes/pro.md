# Week 5 on the pro route

**No helpers, one real constraint.** `app/trace.py` and `app/guard.py` are signatures only. The
constraint: **one attack that the pattern filter cannot catch** (another language, an encoding, a
paraphrase) must be added to `eval/attacks.jsonl` and *held* by a defence you can name, **and**
the MCP server must enforce a per-token daily budget.
