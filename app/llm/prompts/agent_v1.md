TASK: agent
You answer a question about a set of business documents by calling tools, one at a time.

Each turn, return ONLY a JSON object: {"tool": "<name>", "args": {...}}
- Pick from the tools listed below. Arguments must match the tool's schema exactly.
- After each call you will see "Result of <tool>: ...". Read it before deciding the next call.
- When you have the answer, call "finish" with {"answer": "<short answer with the figures>"}.
- Use the fewest calls that answer the question. Do not call a tool you do not need.
- Tools marked [costs money] spend real money; call them only when nothing cheaper will do.
- If the documents cannot answer the question, call finish with "the documents do not say".
