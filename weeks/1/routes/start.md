# Week 1 on the start route

**Faults named, worked examples given.** `app/api/extract.py` and `app/tools/desk.py` are stubs
whose comments name each thing that goes wrong if you skip it. `retry.py`, `structured.py` and
`cost.py` are given and working.

Two worked examples, each solving a *different, smaller* thing in full:

```
uv run python weeks/1/routes/worked_example.py        # an endpoint: language detection
uv run python weeks/1/routes/worked_example_tool.py   # a tool: document_info, designed in full
```

Read each, run it, then build yours the same way. The tool example shows every part your two
tools need: a description that says when to call it, an argument with a description and a
constraint, only the fields the caller needs, and a refusal in words. Use an unblock call as soon
as you are stuck for more than an hour.
