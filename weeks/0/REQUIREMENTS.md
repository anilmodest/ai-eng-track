# What the finished system must do

Twelve requirements. Each one is demonstrable, and each is checked either automatically or at the
final session. This is the specification you are being measured against. Read it in week 0; none
of it should be a surprise in week 6.

| | Requirement | How it is demonstrated | Built in |
| --- | --- | --- | --- |
| **O1** | **Answers the right version.** Given a question and a customer version, the answer is drawn only from documentation for that version | A version 3 question returns zero version 2 source material, tested | Week 2 |
| **O2** | **Declines rather than invents.** When nothing retrieved clears the relevance threshold, the system says it does not know | Decline rate on the unanswerable test questions is at or above the defined floor | Week 3 |
| **O3** | **Cites its source.** Every answer names the document and section it came from | Every returned citation resolves to a stored section | Week 3 |
| **O4** | **Reports its own accuracy.** Decline rate on unanswerable questions, faithfulness, and accuracy on version-dependent questions — computed by running a command | The command runs and prints the three numbers | Week 3 |
| **O5** | **Blocks its own regressions.** The evaluation runs on every proposed change and fails the change if the score drops | A seeded bad change is demonstrated being blocked | Week 3 |
| **O6** | **Survives the model misbehaving.** Timeout, retry on transient failures only, one repair attempt on malformed output, then a typed error. Never an unhandled crash | Checks against a fake provider with scripted failures | Week 1 |
| **O7** | **Never pays twice.** A repeated question against the same document, provider, model and prompt version is served from storage with zero provider calls | Provider call count is 1 after two identical requests | Week 1 |
| **O8** | **Is provider-independent.** The provider is changed by configuration, with no code difference | Swap demonstrated live, with an empty difference in provider-specific code | Week 1 |
| **O9** | **Knows what it costs and what went wrong.** Cost and latency recorded per call and attributed per step, a cost-per-question view, and failures classified rather than logged as one category | A traced request records a non-null duration and cost for every step, and failures are shown grouped by class | Weeks 1 and 5 |
| **O10** | **Reaches a real system safely.** One tool interface that looks up a customer's version, scoped to read one record, no writes | A call outside the scope is refused, and the refusal is tested | Week 4 |
| **O11** | **Resists instructions hidden in documents.** An injection planted in a retrieved document does not change what the system does | The injection test fails before the defence and passes after it | Week 5 |
| **O12** | **Runs where someone else can use it.** A published, versioned build with a rollback demonstrated | Someone who never built it can run it and get a correct, cited answer | Week 6 |

## Deliberately not required

Training or fine-tuning a model. Multi-agent systems. Production-grade latency or throughput
guarantees. User authentication or multi-tenancy. Any paid infrastructure.

A cost ceiling or latency budget on the pro route is a different thing: it is there to force a
design decision, not to certify performance.

## One thing the programme expects that it does not ship

The three-way comparison in week 4 exists to produce a *decision*, not a feature. The recommended
outcome is that no agent goes into the finished system. Being able to say why, with your own
numbers, is worth more in an interview than having built one.
