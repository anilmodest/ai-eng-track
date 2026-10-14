# Your role, and the rules

## Your role

You are the AI engineer on a small support-tools team. You own one service: you build it in week 1
and improve it every week after. Your mentor plays the reviewer from the support desk. You make the
engineering decisions and explain each one; the desk decides whether the answers would help them in
practice.

What you produce by the end: a service someone else can run, a repository showing six weeks of
work with its test results, and one page saying what the thing did for the business.

## What you need before week 1

- Python beyond notebooks, including writing tests
- Having built a small web service of some kind
- Basic SQL, and reading and writing JSON
- Git branches and pull requests
- Having run an application in a container at least once
- AI Fluency completed

You do not need to have built anything with a model before. That is what this is for.

## What is fixed

- **Six weeks**, 55 to 63 hours in all (week 0 about 5, weeks 1 to 6 about 8 to 10 each, weeks 3
  and 4 the heaviest). Weeks 2, 4 and 5 have no session.
- **Four sessions**: discovery, direction at the end of week 1, observation at the end of week 3,
  defence at the end of week 6. From session 2, each has a half where you drive your own AI
  assistant on something unseen and a half with tools closed.
- **Your route** is set from the discovery task: your mentor recommends it, the programme lead
  confirms it, and you make your repository from that route's template. You do not choose it. It
  can be corrected once, at session 2; the programme then opens a pull request on your repository
  that swaps the files for the weeks still ahead. Nobody else ever types in your repository.
- **One pull request a week**, from `week-N` to `main`, sent 24 hours before a session in the weeks
  that have one.

## Seven rules that hold every week

1. **Every week runs on a free tier.** You never pay for a model. The programme's hidden evaluation
   runs on its own key, on one fixed model, so everyone is measured the same way.
2. **Every number is reproducible by a command.** `make evidence WEEK=N` runs the week's
   measurements on a real model and writes `evidence/week-N.json`, with the commit, provider and
   model. A pasted table is not evidence.
3. **Cost and latency are recorded from week 1.** Before they matter, so it is a habit.
4. **One branch and one pull request per week.** The checks gate the merge; the history is the
   record.
5. **A stranger can run it from a clean start**, following the written instructions alone.
6. **Every week ends in a decision record**, `decisions/week-N.md` from `DECISION_TEMPLATE.md`.
   The gate checks that it exists, that it names an option you rejected, and that every number in
   it is the number in your evidence file. An assistant can write prose; it cannot produce the
   measurement the prose has to match.
7. **Use an AI assistant, log it, and own the result.** `ai-use/week-N.yml` from
   `AI_USE_TEMPLATE.yml`, kept as you go. Every line must be explainable at a session.

## Using AI tools

Use them. You are building an AI product; pretending you would not use one to do it is theatre,
and the job you are preparing for expects you to.

Three conditions:

1. **You can explain every line.** At any session your mentor may point at a function you did not
   write by hand and ask what it does, why it is there, and what breaks if it is removed. "The
   tool wrote it" ends that conversation badly.
2. **You check what it gives you.** It will be confidently wrong about this codebase, because it
   cannot see your test failures or your measurements. Q4 of the reflection asks what you did to
   check; answer it with what you actually ran or read.
3. **You say what you used.** In `ai-use/week-N.yml`, as you go: the tool, what you asked, what
   it produced, what you checked, and whether you kept it. Q5 of the reflection is the summary.

Only one thing fails this programme outright: **submitting help you did not disclose.** Not a
red gate, not a missed week, not a wrong answer defended honestly. A green gate on work that is
not yours teaches you nothing and tells an employer something untrue.

## What happens if you cannot defend the work

You complete the track. The gap is recorded honestly and stated plainly. That is deliberate: this
is a programme, not an exam, and an honest record is worth more to you than a flattering one.
