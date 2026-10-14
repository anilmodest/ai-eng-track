# Glossary

One plain sentence per term. The last column is the week that teaches it properly; until then,
this sentence is enough.

| Term | What it means | Week |
| --- | --- | --- |
| Abstention | The system declining to answer because nothing it retrieved is good enough, instead of guessing. Also called declining. | 3 |
| Agent | A system where the model chooses its own next step, such as which tool to call, rather than following steps you wrote. | 1, 4 |
| Agent loop | The cycle of model decides, tool runs, result goes back to the model, repeated until done or stopped by a step or cost limit. | 4 |
| Approval | A person confirming an action before it happens. Enforced in code: the tool returns "needs approval" and the loop stops. | 4 |
| Blast radius | The worst thing that can happen if a defence fails, given what the system is able to do. | 5 |
| Chunk, chunking | Cutting documents into pieces small enough to search and to show the model. How you cut changes what is found. | 2 |
| Citation | The document and section an answer came from, so the user can check it. | 3 |
| Context, context window | Everything the model is shown on one request. The window is the most it can take; filling it is not the same as helping it. | 2 |
| Context engineering | Deciding exactly what the model is shown on each request, and what to leave out. | 2 |
| Cost attribution | Knowing what each step of a request cost, so you can say what a ticket costs and where the money goes. | 1, 5 |
| Decision record | Your one-page weekly note: the decision, the options, the numbers, what you rejected and the risk you accepted. | All |
| Decline rate | How often the system declines. Measured separately on questions that have no answer and on questions that do. | 3 |
| Embedding, dense search | Turning text into numbers that capture meaning, then finding the pieces closest in meaning to the question. | 2 |
| Evaluation, test set | A fixed set of questions with known answers, run on every change, so you know whether a change helped or hurt. | 3 |
| Faithfulness | Whether every claim in an answer is supported by the text the system retrieved. | 3 |
| Function calling, tool schema | The model asking for a tool to be run by returning structured arguments. The schema describes the tool and its arguments, and the description is effectively a prompt. | 1 |
| Grounding | Making the model answer only from the text you gave it, not from what it learned in training. | 3 |
| Hidden test set | Questions the programme holds and you never see. It reports totals on your pull request, so you cannot tune to it. | 3 |
| Hybrid search | Combining keyword search with meaning-based search, because each misses what the other finds. Reciprocal rank fusion merges the two lists. | 2 |
| Idempotency | Safe to repeat: the same request twice does not do the work, or charge you, twice. | 1 |
| Judge | A model used to grade answers, for example for faithfulness. Trusted only after you check how often it agrees with your own labels. | 3 |
| Keyword search, BM25 | Finding pieces that share the question's words. Strong on product codes, error numbers and setting names. | 2 |
| Least agency | Giving the system only the abilities it needs, so a successful attack can do little. | 4, 5 |
| MCP | Model Context Protocol: a standard way to serve tools to a model. It carries the calls; it does not decide what is allowed. | 4 |
| Metadata filtering | Searching only inside pieces with a given label, such as version 3. The fix for the version trap. | 2 |
| Observability, tracing, span | Recording what happened on each request so it can be explained afterwards. A span is one timed, costed step in that record. | 5 |
| Personal-data masking | Replacing names, emails and phone numbers before text reaches the model, and restoring them only in approved output. | 5 |
| Precision, recall, hit rate, MRR | Four ways of scoring whether retrieval found the right pieces. See [worked example A](worked-examples.md#example-a-retrieval-metrics-week-2). | 2 |
| Prompt injection | Instructions hidden in content the system reads, a document or a customer's ticket, aimed at making it do something it should not. | 5 |
| Regression gate | The check that blocks a change from merging if it makes the scores worse. | 3 |
| Retrieval | Finding the few relevant pieces of your documents and showing them to the model with the question. | 2 |
| Routing table | Your week 4 decision, per task type: plain code, a fixed workflow or an agent, and a cheap or frontier model, with the numbers behind it. | 4 |
| Structured output | Asking the model for data in a fixed shape and validating it, here with Pydantic, instead of trusting free text. | 1 |
| Trajectory | The path an agent took: which tools, in which order, how many steps, and whether it acted without approval. | 3, 4 |
| Version trap | The version 2 and version 3 pages read almost the same, so similarity alone finds the wrong one and the answer is confidently wrong. | 2 |
