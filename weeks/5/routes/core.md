# Week 5 on the core route

**Faults present, not located, count not given.** The guard, `app/privacy.py` and
`app/agents/routing.py` are written with mistakes planted, and `app/trace.py` is signatures only:
you instrument the service yourself. One planted fault lets a phone number through that the gate
never tests for; one offers a capability a request never asked for. Review before you run, and
record what you found and how in `ai-use/week-5.yml`.
