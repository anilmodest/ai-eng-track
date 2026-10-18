# What the finished system must do

Sixteen requirements. Each one is demonstrable, and each one is checked automatically by your
gate, by the programme's hidden evaluation, or at the final session. This is the specification you
are being measured against. Read it in week 0; none of it should be a surprise in week 6.

| | Requirement | How it is demonstrated | Built in |
| --- | --- | --- | --- |
| **O1** | **Answers the right version.** Given a question and a customer version, the answer is drawn only from documentation for that version | A version 3 question returns zero version 2 source material, tested | Week 2 |
| **O2** | **Declines rather than invents.** When nothing retrieved clears the relevance threshold, the system says it does not know, and the ticket goes to a person instead | Decline rate on the unanswerable questions, yours and the hidden set's, is at or above the defined floor | Week 3 |
| **O3** | **Cites its source.** Every answer names the document and section it came from | Every returned citation resolves to a stored section | Week 3 |
| **O4** | **Reports its own accuracy.** Decline rate, faithfulness and accuracy on version-dependent questions, computed by running a command, with a judge whose agreement with human labels you measured | The command runs and prints the numbers; the programme runs the same measures on its hidden set for each week you merge | Week 3 |
| **O5** | **Blocks its own regressions.** The evaluation runs on every proposed change and fails the change if the score drops | A seeded bad change is demonstrated being blocked | Week 3 |
| **O6** | **Survives the model misbehaving.** Timeout, retry on transient failures only, one repair attempt on malformed output, then a typed error. Never an unhandled crash | Checks against a fake provider with scripted failures | Week 1 |
| **O7** | **Never pays twice.** A repeated question against the same document, provider, model and prompt version is served from storage with zero provider calls | Provider call count is 1 after two identical requests | Week 1 |
| **O8** | **Is provider-independent.** The provider is changed by configuration, with no code difference, and it runs on any model that meets the standard in `docs/models.md` | Swap demonstrated live, with an empty difference in provider-specific code | Week 1 |
| **O9** | **Knows what it costs and what went wrong.** Cost and latency per step, as spans named the way OpenTelemetry names model and tool calls, a cost-per-ticket view, and failures classified rather than logged as one category | A traced request records a non-null duration and cost for every step, tool calls included, and failures are shown grouped by class | Weeks 1 and 5 |
| **O10** | **Reaches real systems safely.** Tools you designed (look up the customer, read a ticket, search the manual, query the ticket data read-only, draft, escalate, credit), also served over MCP, with scopes enforced in code | A call outside a tool's scope is refused, and the refusal is tested, for every tool | Weeks 1 and 4 |
| **O11** | **Resists instructions hidden in content.** An injection planted in a retrieved document, or in a ticket a tool returns, does not change what the system does | The injection test fails before the defence and passes after it; the programme runs its own attack set on the week you merge | Week 5 |
| **O12** | **Runs where someone else can use it.** A versioned container image anyone can run, with a rollback demonstrated. A public URL is optional | The released image returns a correct, cited answer to a supplied question; rollback to the previous tag demonstrated | Week 6 |
| **O13** | **Acts only with approval.** Any action that writes, spends or reaches a customer stops for a person's approval, credits are capped per ticket, and every action taken is recorded | Zero unapproved actions on your trajectory tasks and on the hidden set; the trace shows the approval, and the desk's records show the action | Week 4 |
| **O14** | **Analyses data without inventing numbers.** Questions about the ticket data are answered by read-only, allowlisted queries, and the number in the answer is the number the query returned | On the analysis tasks, every stated number matches the data; an answer with a number no tool returned is not accepted | Week 4 |
| **O15** | **Keeps personal data away from the model.** Names, emails and phone numbers in tickets are masked before any model call and restored only in what a person reads | A test asserts that no unmasked personal data appears in any recorded model input | Week 5 |
| **O16** | **Is measured as an agent.** Tool-choice accuracy, steps per task, cost per task and approval violations, on twenty trajectory tasks | The trajectory evaluation runs by command and in the gate, and its numbers sit beside the answer-quality numbers | Weeks 3 and 4 |

## Deliberately not required

Training or fine-tuning a model. Multi-agent systems. Production-grade latency or throughput
guarantees. User authentication or multi-tenancy. Any paid infrastructure. GPU programming,
quantisation and on-device inference: they belong to a different track.

A cost ceiling or latency budget on the pro route is a different thing: it is there to force a
design decision, not to certify performance.

## Where agency goes is a decision, not a default

The three-way comparison in week 4 (plain code, a fixed workflow, an agent) ends in a decision, task
type by task type: where agency pays and where it does not, and which model each task deserves.
"No agent" is a good answer for a task type when your numbers say so. It is not the expected answer
for the whole system, because this brief has steps that need judgement. Being able to say which
is which, with your own numbers, is what an interviewer is asking for.
